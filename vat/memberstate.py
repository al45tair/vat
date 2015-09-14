# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
from decimal import Decimal as d
import datetime
import re
from .rates import RateCache

_alpha_2_map = {}
_code_map = {}
_rate_cache = RateCache()

class Threshold(object):
    def __init__(self, currency, amount):
        self.currency = currency
        self.amount = amount

class MemberState(object):
    """Represents and holds information about an EU member state."""
    def __init__(self, code, iso_alpha_2, name,
                 currency,
                 special_scheme_threshold,
                 distance_selling_threshold,
                 small_enterprise_threshold,
                 number_format):
        def to_rate(x):
            if x is None:
                return None
            return decimal.Decimal('%.1f' % x) / 100
        def to_rates(x):
            if x is None:
                return None
            if not isinstance(x, (tuple, list)):
                return to_rates((x, ))
            result = []
            for y in x:
                result.append(to_rate(y))
            return tuple(result)
        def to_threshold(x):
            if x is None:
                return None
            if isinstance(x, (tuple, list)):
                result = []
                for y in x:
                    currency, amount = y.split(' ')
                    result.append(Threshold(currency, decimal.Decimal(amount)))
                return tuple(result)
            currency, amount = x.split(' ')
            return Threshold(currency, decimal.Decimal(amount))

        # The VAT country code (e.g. Greece is 'EL')
        self.code = code

        # The ISO 3166 alpha-2 code (e.g. Greece is 'GR')
        self.iso_alpha_2 = iso_alpha_2

        # The name of this Member State (in English)
        self.name = name

        # A regular expression (as a string) matching the VAT number format
        self.number_regex = '^(%s)$' % number_format
        
        # A re.RegexObject matching the VAT number format
        self.number_format = re.compile(self.number_regex)

        # The currency used in this Member State
        self.currency = currency

        # The special scheme threshold (a Threshold object)
        self.special_scheme_threshold = to_threshold(special_scheme_threshold)

        # The distance selling threshold (a Threshold object)
        self.distance_selling_threshold = to_threshold(distance_selling_threshold)

        # The small enterprise threshold (a Threshold object)
        self.small_enterprise_threshold = to_threshold(small_enterprise_threshold)
        
        _alpha_2_map[iso_alpha_2] = self
        _code_map[code] = self

    @property
    def standard_rate(self):
        return _rate_cache.standard_rate(self.code).rate / 100

    @property
    def reduced_rates(self):
        return tuple([r.rate/100 for r in _rate_cache.reduced_rates(self.code) if r.detail not in ('Super Reduced', 'Parking')])

    @property
    def super_reduced_rate(self):
        for r in _rate_cache.reduced_rates(self.code):
            if r.detail == 'Super Reduced':
                return r.rate / 100
        return None

    @property
    def parking_rate(self):
        for r in _rate_cache.reduced_rates(self.code):
            if r.detail == 'Parking':
                return r.rate / 100
        return None
    
    @staticmethod
    def by_code(code):
        return _code_map[code]

    @staticmethod
    def by_iso_alpha_2(alpha_2):
        return _alpha_2_map[alpha_2]
    
MS = MemberState

### Make your window *REALLY WIDE* before editing below.

# Sources:
# http://ec.europa.eu/taxation_customs/resources/documents/taxation/vat/how_vat_works/rates/vat_rates_en.pdf
# http://ec.europa.eu/taxation_customs/resources/documents/taxation/vat/traders/vat_community/vat_in_ec_annexi.pdf

# 2015-01-01: There have been changes to the thresholds since the above Annex I document was last updated.
#             Notably, Lithuania is now part of the Euro zone, so I've updated its entry in the table to
#             reflect that change.  Unfortunately, there does not appear to be any obvious source of
#             information on the thresholds that now apply (since LTL is no longer in use); I've rounded
#             to the nearest round Euro amount for now.

# 2015-07-15: There were rate changes for Luxembourg on 2015-03-31

# 2015-09-14: Removed VAT rates from this code in favour of using the EU's web service to retrieve them.

# Update these dates when you update the table below; they should reflect the dates of the update, not any dates
# you might see on the documents above.
vat_rate_update_date = datetime.date.today()
threshold_update_date = datetime.date(2015, 1, 1)

# ********************************************************************************************************************
# *                                                                                                                  *
# *   N.B. It is your responsibility to choose the correct rate, which might vary depending on what you're selling.  *
# *        It is also your responsibility to choose the correct threshold.                                           *
# *                                                                                                                  *
# *        The maintainer of this package takes NO RESPONSIBILITY for any typos or inaccuracies contained below, or  *
# *        for any mistakes you might make using the data contained herein.                                          *
# *                                                                                                                  *
# ********************************************************************************************************************

# All member states, along with their VAT information.  Note that some countries have multiple small VAT thresholds; note also Hungary, which quotes
# its special and distance thresholds in Euros even though it uses the Forint.
member_states = [
    #  code  iso   name               currency  thresholds                                            number format
    #                                                  special          distance             small
    MS('BE', 'BE', 'Belgium',         'EUR',     'EUR 11200.00',   'EUR 35000.00',   'EUR 15000.00',  r'\d{10}'),
    MS('BG', 'BG', 'Bulgaria',        'BGN',     'BGN 20000.00',   'BGN 70000.00',   'BGN 50000.00',  r'\d{9,10}'),
    MS('CZ', 'CZ', 'Czech Republic',  'CZK',    'CZK 326000.00', 'CZK 1140000.00', 'CZK 1000000.00',  r'\d{8,10}'),
    MS('DK', 'DK', 'Denmark',         'DKK',     'DKK 80000.00',  'DKK 280000.00',   'DKK 50000.00',  r'(?:\d{2}\s*){3}\d{2}'),
    MS('DE', 'DE', 'Germany',         'EUR',     'EUR 12500.00',  'EUR 100000.00',   'EUR 17500.00',  r'\d{9}'),
    MS('EE', 'EE', 'Estonia',         'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 16000.00',  r'\d{9}'),
    MS('EL', 'GR', 'Greece',          'EUR',     'EUR 10000.00',   'EUR 35000.00',   ('EUR 5000.00',
                                                                                     'EUR 10000.00'), r'\d{9}'),
    MS('ES', 'ES', 'Spain',           'EUR',     'EUR 10000.00',   'EUR 35000.00',            None,   r'[A-Z\d]\d{7}[A-Z\d]'),
    MS('FR', 'FR', 'France',          'EUR',     'EUR 10000.00',  'EUR 100000.00',  ('EUR 34900.00',
                                                                                     'EUR 90300.00'), r'[A-Z\d]{2}\s*\d{9}'),
    MS('HR', 'HR', 'Croatia',         'HRK',     'HRK 77000.00',  'HRK 270000.00',  'HRK 230000.00',  r'\d{11}'),
    MS('IE', 'IE', 'Ireland',         'EUR',     'EUR 41000.00',   'EUR 35000.00',  ('EUR 37500.00',
                                                                                     'EUR 75000.00'), r'\d[A-Z\d+*]\d{5}[A-Z]{1,2}'),
    MS('IT', 'IT', 'Italy',           'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 30000.00',  r'\d{11}'),
    MS('CY', 'CY', 'Cyprus',          'EUR',     'EUR 10251.00',   'EUR 35000.00',   'EUR 15600.00',  r'\d{8}[A-Z]'),
    MS('LV', 'LV', 'Latvia',          'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 50000.00',  r'\d{11}'),
    MS('LT', 'LT', 'Lithuania',       'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 45000.00',  r'\d{9}(?:\d{3})?'),
    MS('LU', 'LU', 'Luxembourg',      'EUR',     'EUR 10000.00',  'EUR 100000.00',   'EUR 25000.00',  r'\d{8}'),
    MS('HU', 'HU', 'Hungary',         'HUF',     'EUR 35000.00',   'EUR 35000.00', 'HUF 6000000.00',  r'\d{8}'),
    MS('MT', 'MT', 'Malta',           'EUR',     'EUR 10000.00',   'EUR 35000.00',  ('EUR 14000.00',
                                                                                     'EUR 24000.00',
                                                                                     'EUR 35000.00'), r'\d{8}'),
    MS('NL', 'NL', 'Netherlands',     'EUR',     'EUR 10000.00',  'EUR 100000.00',            None,   r'\d{9}B\d{2}'),
    MS('AT', 'AT', 'Austria',         'EUR',     'EUR 11000.00',   'EUR 35000.00',   'EUR 30000.00',  r'U\d{8}'),
    MS('PL', 'PL', 'Poland',          'PLN',     'PLN 50000.00',  'PLN 160000.00',  'PLN 150000.00',  r'\d{10}'),
    MS('PT', 'PT', 'Portugal',        'EUR',     'EUR 10000.00',   'EUR 35000.00',  ('EUR 10000.00',
                                                                                     'EUR 12500.00'), r'\d{9}'),
    MS('RO', 'RO', 'Romania',         'RON',     'RON 34000.00',  'RON 118000.00',  'RON 220000.00',  r'\d{2,10}'),
    MS('SI', 'SI', 'Slovenia',        'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 50000.00',  r'\d{8}'),
    MS('SK', 'SK', 'Slovakia',        'EUR',     'EUR 13941.00',   'EUR 35000.00',   'EUR 49790.00',  r'\d{10}'),
    MS('FI', 'FI', 'Finland',         'EUR',     'EUR 10000.00',   'EUR 35000.00',    'EUR 8500.00',  r'\d{8}'),
    MS('SE', 'SE', 'Sweden',          'SEK',     'SEK 90000.00',  'SEK 320000.00',            None,   r'\d{12}'),
    MS('GB', 'GB', 'United Kingdom',  'GBP',     'GBP 81000.00',   'GBP 70000.00',   'GBP 81000.00',  r'\d{3}\s*\d{4}\s*\d{2}(?:\s*\d{3})?|GD\d{3}|HA\d{3}'),
    ]
    
