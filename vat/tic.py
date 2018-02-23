# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal as D
import re
import datetime
from six.moves import urllib
from lxml.html import soupparser

from .vrws import Rate, Rates

TIC_VATRATESEARCH = str('http://ec.europa.eu/taxation_customs/tic/public/vatRates/vatratesSearch.html')


def format_date(date):
    return '{d:02d}/{m:02d}/{y:04d}'.format(y=date.year,
                                            m=date.month,
                                            d=date.day)


class TICException(Exception):
    pass


class TICHTTPException(TICException):
    def __init__(self, code, headers, body):
        self.code = code
        self.headers = headers
        self.body = body

    def __repr__(self):
        return 'TICHTTPException(%r, %r, %r)' % (self.code,
                                                 self.headers,
                                                 self.body)


msa_map = {
    'AT': 1,
    'BE': 2,
    'BG': 3,
    'CY': 4,
    'CZ': 5,
    'DE': 6,
    'DK': 7,
    'EE': 8,
    'EL': 9, 'GR': 9,
    'ES': 10,
    'FI': 11,
    'FR': 12,
    'GB': 13, 'UK': 13,
    'HR': 14,
    'HU': 15,
    'IE': 16,
    'IT': 17,
    'LT': 18,
    'LU': 19,
    'LV': 20,
    'MT': 21,
    'NL': 22,
    'PL': 23,
    'PT': 24,
    'RO': 25,
    'SE': 26,
    'SI': 27,
    'SK': 28
    }


_percent_re = re.compile('(\d*(?:\.\d*)?)%')


def get_rates(country, date=None):
    """Retrieve the VAT rates for the specified country.  Returns a
       Rates object on success, or in case of error raises an exception."""

    if date is None:
        date = datetime.date.today()

    req = urllib.request.Request(
        url=TIC_VATRATESEARCH,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})
    req.method = 'POST'
    req.data = urllib.parse.urlencode([
        ('listOfMsa', msa_map[country]),
        ('listOfTypes', 'Standard'),
        ('listOfTypes', 'Reduced'),
        ('listOfTypes', 'Category'),
        ('dateFilter', format_date(date))])

    f = urllib.request.urlopen(req)

    status = f.getcode()

    if status != 200:
        raise TICHTTPException(status, f.info(), f.read())

    body = f.read()

    xml = soupparser.fromstring(body)

    row = xml.find('.//div[@id="national"]/table/tbody/tr')
    std_rate = ''.join(row[1].itertext()).strip()

    m = _percent_re.match(std_rate)

    if not m:
        raise TICException("didn't understand rate %s" % std_rate)

    rate = Rate(D(m.group(1)), date)
    rates = Rates({'Standard': rate}, {}, {})

    return rates
