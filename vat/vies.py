# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import urllib
import datetime
import xml.sax.saxutils
import time
import six
from six.moves import http_client
from dateutil import tz
from lxml import etree

VIES_HOST = str('ec.europa.eu')
VIES_PATH = str('/taxation_customs/vies/services/checkVatService')

class VIESException(Exception):
    pass

_vies_fault_re = re.compile(r'/(INVALID_INPUT|SERVICE_UNAVAILABLE|MS_UNAVAILABLE|TIMEOUT|SERVER_BUSY)/')

class VIESSOAPException(VIESException):
    def __init__(self, code, string, actor, detail):
        self.code = code
        self.string = string
        self.actor = actor
        self.detail = detail

        m = _vies_fault_re.search(string)
        if m:
            self.fault_type = m.group(0)
        else:
            self.fault_type = 'UNKNOWN'

    @classmethod
    def from_fault(cls, fault):
        def contents(name):
            value = fault.find('./' + SOAP_NS + name)
            if value is None:
                value = fault.find('./' + name)
            if value is not None:
                value = value.text
            return value

        faultcode = contents('faultcode')
        faultstring = contents('faultstring')
        faultactor = contents('faultactor')
        detail = contents('detail')

        return cls(faultcode, faultstring, faultactor, detail)

    def __repr__(self):
        return 'VIESSOAPException(%r, %r, %r, %r)' % (self.code,
                                                      self.string,
                                                      self.actor,
                                                      self.detail)

    def __unicode__(self):
        return '%s - %s (%s)\n%s' % (self.code, self.string, self.actor, self.detail)

    def __str__(self):
        return str(self.__unicode__())
    
class VIESHTTPException(VIESException):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return 'VIESHTTPException(%r, %r)' % (self.code, self.message)

    def __unicode__(self):
        return '%s - %s' % (self.code, self.message)

    def __str__(self):
        return str(self.__unicode__())
    
class VIESResponseBase(object):
    def __init__(self, country, vat_number, request_date, valid):
        self.country = country
        self.vat_number = vat_number
        self.request_date = request_date
        self.valid = valid
    
class VIESResponse(VIESResponseBase):
    def __init__(self, country, vat_number, request_date,
                 valid, name, address):
        super(VIESResponse, self).__init__(country, vat_number,
                                           request_date, valid)
        self.name = name
        self.address = address

    def __repr__(self):
        return 'VIESResponse(%r, %r, %r, %r, %r, %r)' % (self.country,
                                                         self.vat_number,
                                                         self.request_date,
                                                         self.valid,
                                                         self.name,
                                                         self.address)
    
class VIESApproxResponse(VIESResponseBase):
    def __init__(self, country, vat_number, request_date, valid,
                 trader_info, trader_match_info, request_id):
        super(VIESApproxResponse, self).__init__(country, vat_number,
                                                 request_date, valid)
        self.trader_info = trader_info
        self.trader_match_info = trader_match_info
        self.request_id = request_id
        
    def __repr__(self):
        return 'VIESApproxResponse(%r, %r, %r, %r, %r, %r, %r)' \
          % (self.country, self.vat_number, self.request_date, self.valid,
             self.trader_info, self.trader_match_info, self.request_id)

_strip_re = re.compile(r'[^A-Za-z0-9]+')
def _strip_vat(vn):
    """Remove any whitespace and punctuation from a VAT number."""
    return _strip_re.sub('', vn)

SOAP_NS = '{http://schemas.xmlsoap.org/soap/envelope/}'
VIES_NS = '{urn:ec.europa.eu:taxud:vies:services:checkVat:types}'

_date_re = re.compile(r'(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})(?:Z|(?P<tzsign>[-+])(?P<tzhours>[0-9]{2}):(?P<tzmins>[0-9]{2}))?$')
def _parse_date(d):
    m = _date_re.match(d)
    if not m:
        return None
    year = int(m.group('year'))
    month = int(m.group('month'))
    day = int(m.group('day'))
    tzsign = m.group('tzsign')
    tzinfo = None
    if tzsign is not None:
        tzhours = int(m.group('tzhours'))
        tzmins = int(m.group('tzmins'))
        tzoffset = (tzhours * 60 + tzmins) * 60
        if tzsign == '-':
            tzoffset = -tzoffset
        tzinfo = tz.tzoffset(None, tzoffset)
    elif d.endswith('Z'):
        tzinfo = tz.tzutc()
    return datetime.datetime(year, month, day, tzinfo=tzinfo)

def _parse_boolean(b):
    if b == 'true' or b == '1':
        return True
    return False

def check_vat(vat_number):
    """Check a VAT number using VIES.  Returns a VIESResponse object on
    success, or in case of error raises an exception."""
    vat_number = _strip_vat(vat_number)
    country_code = vat_number[:2]
    number = vat_number[2:]

    message = '''<?xml version="1.0" encoding="UTF-8" ?>
<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
 env:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <env:Body xmlns:vies="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
    <vies:checkVat>
      <vies:countryCode>%s</vies:countryCode>
      <vies:vatNumber>%s</vies:vatNumber>
    </vies:checkVat>
  </env:Body>
</env:Envelope>''' % (country_code, number)
    message = message.encode('utf-8')
    
    headers = { b'Content-type': b'text/xml',
                b'SOAPAction': b'urn:ec.europa.eu:taxud:vies:services:checkVat' }

    tries = 0
    response = None
    while response is None or (tries < 5
                               and response.status >= 500
                               and response.status <= 599):
        if tries > 0:
            time.sleep(tries)
        tries += 1
        conn = http_client.HTTPConnection(VIES_HOST)
        conn.request(str('POST'), VIES_PATH, message, headers)
        response = conn.getresponse()

    if response.status != 200:
        raise VIESHTTPException(response.status, response.reason)

    tree = etree.parse(response)
    root = tree.getroot()

    if root.tag.lower() != SOAP_NS + 'envelope':
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    fault = root.find('./' + SOAP_NS + 'Body/' + SOAP_NS + 'Fault')

    if fault is not None:
        raise VIESSOAPException.from_fault(fault)

    resp = root.find('./' + SOAP_NS + 'Body/' + VIES_NS + 'checkVatResponse')

    if resp is None:
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    country_code = resp.find('./' + VIES_NS + 'countryCode').text
    number = resp.find('./' + VIES_NS + 'vatNumber').text
    request_date = _parse_date(resp.find('./' + VIES_NS + 'requestDate').text)
    valid = _parse_boolean(resp.find('./' + VIES_NS + 'valid').text)
    name = resp.find('./' + VIES_NS + 'name').text
    address = resp.find('./' + VIES_NS + 'address').text

    if name == '---':
        name = None
    if address == '---':
        address = None
    
    return VIESResponse(country_code, number, request_date, valid, name, address)

_eltnames = {
    'name': 'traderName',
    'company-type': 'traderCompanyType',
    'street': 'traderStreet',
    'postcode': 'traderPostcode',
    'city': 'traderCity'
    }

_respeltnames = {
    'traderName': 'name',
    'traderCompanyType': 'company-type',
    'traderAddress': 'address',
    'traderStreet': 'street',
    'traderPostcode': 'postcode',
    'traderCity': 'city'
    }

_respmatchnames = {
    'traderNameMatch': 'name',
    'traderCompanyTypeMatch': 'company-type',
    'traderStreetMatch': 'street',
    'traderPostcodeMatch': 'postcode',
    'traderCityMatch': 'city',
    }

MATCH_VALID = 'valid'
MATCH_INVALID = 'invalid'
MATCH_NOT_PROCESSED = 'not-processed'

_matchcodes = {
    1: MATCH_VALID,
    2: MATCH_INVALID,
    3: MATCH_NOT_PROCESSED
    }

def check_vat_approx(vat_number, extra={}, requester=None):
    """Check a VAT number using VIES, passing in additional information about
    the entity being checked.  Returns a VIESApproxResponse object on
    success, or in case of error raises an exception.

    The keys in the `extra` dictionary are as follows:

      name
      company-type
      street
      postcode
      city

    All keys are optional.

    You can also pass in the VAT number of the requesting entity; this too
    is optional."""

    vat_number = _strip_vat(vat_number)
    country_code = vat_number[:2]
    number = vat_number[2:]

    extra_tags = []
    for k,v in six.iteritems(extra):
        t = _eltnames.get(k, None)
        if t:
            v = xml.sax.saxutils.escape(v, { "'": '&#x2019;' })
            extra_tags.append('<vies:%s>%s</vies:%s>' % (t, v, t))

    if requester:
        requester = _strip_vat(requester)
        req_cc = requester[:2]
        req_num = requester[2:]
        extra_tags.append('<vies:requesterCountryCode>%s</vies:requesterCountryCode><vies:requesterVatNumber>%s</vies:requesterVatNumber>' % (req_cc, req_num))
            
    message = '''<?xml version="1.0" encoding="UTF-8" ?>
<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
 env:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <env:Body xmlns:vies="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
    <vies:checkVatApprox>
      <vies:countryCode>%s</vies:countryCode>
      <vies:vatNumber>%s</vies:vatNumber>%s
    </vies:checkVatApprox>
  </env:Body>
</env:Envelope>''' % (country_code, number, '\n'.join(extra_tags))
    message = message.encode('utf-8')

    headers = { b'Content-type': b'text/xml',
                b'SOAPAction': b'urn:ec.europa.eu:taxud:vies:services:checkVatApprox' }

    tries = 0
    response = None
    while response is None or (tries < 5
                               and response.status >= 500
                               and response.status <= 599):
        if tries > 0:
            time.sleep(tries)
        tries += 1
        conn = http_client.HTTPConnection(VIES_HOST)
        conn.request(str('POST'), VIES_PATH, message, headers)
        response = conn.getresponse()
    
    if response.status != 200:
        raise VIESHTTPException(response.status, response.reason)

    tree = etree.parse(response)
    root = tree.getroot()

    if root.tag.lower() != SOAP_NS + 'envelope':
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    fault = root.find('./' + SOAP_NS + 'Body/' + SOAP_NS + 'Fault')

    if fault is not None:
        raise VIESSOAPException.from_fault(fault)

    resp = root.find('./' + SOAP_NS + 'Body/' + VIES_NS
                     + 'checkVatApproxResponse')

    if resp is None:
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    country_code = resp.find('./' + VIES_NS + 'countryCode').text
    number = resp.find('./' + VIES_NS + 'vatNumber').text
    request_date = _parse_date(resp.find('./' + VIES_NS + 'requestDate').text)
    valid = _parse_boolean(resp.find('./' + VIES_NS + 'valid').text)
    request_id = resp.find('./' + VIES_NS + 'requestIdentifier').text
    
    info = {}
    for t,k in six.iteritems(_respeltnames):
        elt = resp.find('./' + VIES_NS + t)
        if elt is not None:
            if elt.text == '---':
                info[k] = None
            else:
                info[k] = elt.text

    match = {}
    for t,k in six.iteritems(_respmatchnames):
        elt = resp.find('./' + VIES_NS + t)
        if elt is not None:
            v = int(elt.text)
            match[k] = _matchcodes.get(v, '<unknown %d>' % v)

    return VIESApproxResponse(country_code, number, request_date, valid,
                              info, match, request_id)
