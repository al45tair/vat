# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
from decimal import Decimal as D
import re
import time
import datetime
import six
from six.moves import http_client
from lxml import etree

# Standard Rate types
STANDARD = 'Standard'
REDUCED = 'Reduced'

# Standard Categories
BROADCASTING = 'Broadcasting Services'
TELECOMS = 'Telecommunication Services'
ESERVICES = 'E-Services'

VRWS_HOST = str('ec.europa.eu')
VRWS_PATH = str('/taxation_customs/tic/services/VatRateWebService')

class VRWSException(Exception):
    pass

_error_re = re.compile(r'^VATRATE-ERR-([0-9]+) - (.*)$')
_date_re = re.compile(r'^([0-9]{2,})-([0-9]{2})-([0-9]{2})$')

class VRWSErrorException(VRWSException):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason

    def __repr__(self):
        return 'VRWSErrorException({code}, {reason})'.format(code=self.code,
                                                             reason=repr(self.reason))

    def __unicode__(self):
        return 'VATRATE-ERR-{code} - {reason}'.format(code=self.code,
                                                      reason=self.reason)

    def __str__(self):
        return str(self.__unicode__())

class VRWSSOAPException(VRWSException):
    def __init__(self, code, string, actor, detail):
        self.code = code
        self.string = string
        self.actor = actor
        self.detail = detail
        
    def __repr__(self):
        return 'VRWSSOAPException(%r, %r, %r, %r)' % (self.code,
                                                      self.string,
                                                      self.actor,
                                                      self.detail)

    def __unicode__(self):
        return '%s - %s (%s)\n%s' % (self.code, self.string, self.actor, self.detail)

    def __str__(self):
        return str(self.__unicode__())    

class VRWSHTTPException(VRWSException):
    def __init__(self, code, message, headers, body):
        self.code = code
        self.message = message
        self.headers = headers
        self.body = body

    def __repr__(self):
        return 'VIESHTTPException(%r, %r, %r, %r)' % (self.code,
                                                      self.message,
                                                      self.headers,
                                                      self.body)

    def __unicode__(self):
        return '%s - %s\n%s\n%s' % (self.code, self.message,
                                    ''.join(['%s: %s\n' % h \
                                             for h in self.headers]),
                                    self.body)

    def __str__(self):
        return str(self.__unicode__())

class Rate(object):
    """Represents an individual VAT rate."""
    def __init__(self, rate, application_date, detail=None):
        # The VAT rate, as a decimal percentage
        self.rate = rate

        # The date from which this rate applies
        self.application_date = application_date

        # Detail, if any; this might indicate a special rate (for instance)
        self.detail = detail

    def __repr__(self):
        return 'Rate(%r, %r, %r)' % (self.rate, self.application_date,
                                     self.detail)

    def __unicode__(self):
        if self.detail:
            return '%g%% (%s, as of %s)' % (self.rate, self.detail,
                                            self.application_date)
        else:
            return '%g%% (as of %s)' % (self.rate, self.application_date)

    def __str__(self):
        return str(self.__unicode__())
        
class Rates(object):
    def __init__(self, types, categories, regions):
        # A dictionary indexed by rate type
        self.types = types

        # A dictionary that contains rates organised by category
        self.categories = categories

        # A dictionary that contains any regional rates that may apply
        self.regions = regions
    
SOAP_NS = '{http://schemas.xmlsoap.org/soap/envelope/}'
VRWS_NS = '{urn:ec.europa.eu:taxud:tic:services:VatRateWebService:types}'
VRWS_NSM = '{urn:ec.europa.eu:taxud:tic:services:VatRateWebService}'

def format_date(date):
    return '{y:04d}-{m:02d}-{d:02d}'.format(y=date.year,
                                            m=date.month,
                                            d=date.day)

def send_message(message):
    message = message.encode('utf-8')

    headers = { b'Content-Type': b'text/xml',
                b'SOAPAction': b'' }

    tries = 0
    response = None
    while response is None or (tries < 5
                               and response.status >= 500
                               and response.status <= 599):
        if tries > 0:
            if response is not None:
                # Cope with badly behaved web service returning 500 for non-
                # server errors
                body = response.read()
                if body.startswith(b'<soap:'):
                    root = etree.fromstring(body)
                    fault = root.find('.//' + SOAP_NS + 'Fault')

                    faultcode = fault.find('./{*}faultcode').text
                    faultstring = fault.find('./{*}faultstring').text
                    faultactor = fault.find('./{*}faultactor')
                    if faultactor is not None:
                        faultactor = faultactor.text
                    detail = fault.find('./{*}detail')
                    if detail is not None:
                        detail = detail.text

                    m = _error_re.match(faultstring)
                    if m:
                        raise VRWSErrorException(int(m.group(1)), m.group(2))
                    
                    raise VRWSSOAPException(faultcode, faultstring,
                                            faultactor, detail)
        
            time.sleep(tries)
        tries += 1
        conn = http_client.HTTPSConnection(VRWS_HOST)
        conn.request(str('POST'), VRWS_PATH, message, headers)
        response = conn.getresponse()

    if response.status != 200:
        raise VRWSHTTPException(response.status, response.reason,
                                response.getheaders(),
                                response.read())

    return response

def parse_response(response, kind):
    tree = etree.parse(response)
    root = tree.getroot()

    if root.tag.lower() != SOAP_NS + 'envelope':
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    resp = root.find('./' + SOAP_NS + 'Body/' + VRWS_NSM + kind)

    if resp is None:
        raise ValueError('Bad SOAP reply "%s"' % etree.tostring(tree))

    types = {}
    categories = {}
    regions = {}
    
    for rate in resp.iter(VRWS_NS + 'rate'):
        rtype = rate.find('./' + VRWS_NS + 'type').text
        rvalue = D(rate.find('./' + VRWS_NS + 'value').text)
        rdate = rate.find('./' + VRWS_NS + 'applicationDate').text
        m = _date_re.match(rdate)
        rdate = datetime.date(int(m.group(1)),
                              int(m.group(2)),
                              int(m.group(3)))
        rrgn = rate.find('./' + VRWS_NS + 'region')
        if rrgn is not None:
            rrgn = rrgn.text
        rcat = rate.find('./' + VRWS_NS + 'category')
        if rcat is not None:
            rcat = rcat.text
        rdetail = rate.find('./' + VRWS_NS + 'detail')
        if rdetail is not None:
            rdetail = rdetail.text
            
        robj = Rate(rvalue, rdate, rdetail)
            
        if rrgn:
            rgn = regions.get(rrgn, None)
            if rgn is None:
                rgn = Rates({}, {}, None)
                regions[rrgn] = rgn
            if rcat:
                rgn.categories.setdefault(rcat, []).append(robj)
            else:
                rgn.types.setdefault(rtype, []).append(robj)
        else:
            if rcat:
                categories.setdefault(rcat, []).append(robj)
            else:
                types.setdefault(rtype, []).append(robj)

    return Rates(types, categories, regions)    

def get_rates(country, date=None,
              fetch_reduced=True, fetch_category=True, fetch_region=True):
    """Retrieve the VAT rates for the specified country.  Returns a
       Rates object on success, or in case of error raises an exception.

       """

    boolean = { True: 'true',
                False: 'false' }

    if date is None:
        date = datetime.date.today()

    fmtdate = format_date(date)

    message = '''<?xml version="1.0" encoding="UTF-8" ?>
<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
 env:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <env:Body
   xmlns:vrwsm="urn:ec.europa.eu:taxud:tic:services:VatRateWebService"
   xmlns:vrws="urn:ec.europa.eu:taxud:tic:services:VatRateWebService:types">
    <vrwsm:ratesRequest>
      <vrws:memberState>{country}</vrws:memberState>
      <vrws:requestDate>{date}</vrws:requestDate>
      <vrws:fetchReduced>{fetch_reduced}</vrws:fetchReduced>
      <vrws:fetchCategory>{fetch_category}</vrws:fetchCategory>
      <vrws:fetchRegion>{fetch_region}</vrws:fetchRegion>
    </vrwsm:ratesRequest>
  </env:Body>
</env:Envelope>'''.format(country=country, date=fmtdate,
                          fetch_reduced=boolean[fetch_reduced],
                          fetch_category=boolean[fetch_category],
                          fetch_region=boolean[fetch_region])

    return parse_response(send_message(message), 'ratesResponse')

def get_changes(from_date=None, to_date=None, country=None):
    """Retrieve a list of VAT rate changes starting from `from_date`."""

    if from_date is None:
        from_date = datetime.date.today()
        
    extras = []
    
    if to_date is not None:
        extras.append('\n      <vrws:dateTo>{to_date}</vrws:dateTo>'\
                      .format(to_date=format_date(to_date)))

    if country is not None:
        extras.append('\n      <vrws:memberState>{country}</vrws:memberState>'\
                      .format(country=country))

    message = '''<?xml version="1.0" encoding="UTF-8" ?>
<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
 env:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <env:Body
   xmlns:vrwsm="urn:ec.europa.eu:taxud:tic:services:VatRateWebService"
   xmlns:vrws="urn:ec.europa.eu:taxud:tic:services:VatRateWebService:types">
    <vrwsm:changesRequest>
      <vrws:dateFrom>{from_date}</vrws:dateFrom>{extras}
    </vrwsm:changesRequest>
  </env:Body>
</env:Envelope>'''.format(from_date=format_date(from_date),
                          extras=''.join(extras))

    return parse_response(send_message(message), 'changesResponse')
    
