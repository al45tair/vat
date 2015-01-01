# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
from decimal import Decimal as d
import datetime
import re

_alpha_2_map = {}
_code_map = {}

class Threshold(object):
    def __init__(self, currency, amount):
        self.currency = currency
        self.amount = amount

class MemberState(object):
    """Represents and holds information about an EU member state."""
    def __init__(self, code, iso_alpha_2, name,
                 standard_rate, reduced_rates,
                 super_reduced_rate, parking_rate,
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

        # The standard VAT rate (e.g. 20% = 0.2)
        self.standard_rate = to_rate(standard_rate)

        # The reduced VAT rates (a tuple, or None)
        self.reduced_rates = to_rates(reduced_rates)

        # The super reduced rate (or None)
        self.super_reduced_rate = to_rate(super_reduced_rate)

        # The "parking" rate (or None)
        self.parking_rate = to_rate(parking_rate)

        # A re.RegexObject matching the VAT number format
        self.number_format = re.compile('^(%s)$' % number_format)

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

# Update these dates when you update the table below; they should reflect the dates of the update, not any dates
# you might see on the documents above.
vat_rate_update_date = datetime.date(2015, 1, 1)
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
    #  code  iso   name               rates                                    currency  thresholds                                            number format
    #                                 standard  reduced        super  parking                   special          distance             small
    MS('BE', 'BE', 'Belgium',         21.0,     (12.0,  6.0),  None,  12.0,    'EUR',     'EUR 11200.00',   'EUR 35000.00',   'EUR 15000.00',  r'\d{10}'),
    MS('BG', 'BG', 'Bulgaria',        20.0,             9.0,   None,  None,    'BGN',     'BGN 20000.00',   'BGN 70000.00',   'BGN 50000.00',  r'\d{9,10}'),
    MS('CZ', 'CZ', 'Czech Republic',  21.0,            15.0,   None,  None,    'CZK',    'CZK 326000.00', 'CZK 1140000.00', 'CZK 1000000.00',  r'\d{8,10}'),
    MS('DK', 'DK', 'Denmark',         25.0,            None,   None,  None,    'DKK',     'DKK 80000.00',  'DKK 280000.00',   'DKK 50000.00',  r'(?:\d{2}\s*){3}\d{2}'),
    MS('DE', 'DE', 'Germany',         19.0,             7.0,   None,  None,    'EUR',     'EUR 12500.00',  'EUR 100000.00',   'EUR 17500.00',  r'\d{9}'),
    MS('EE', 'EE', 'Estonia',         20.0,             9.0,   None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 16000.00',  r'\d{9}'),
    MS('EL', 'GR', 'Greece',          23.0,     (13.0,  6.5),  None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   ('EUR 5000.00',
                                                                                                                              'EUR 10000.00'), r'\d{9}'),
    MS('ES', 'ES', 'Spain',           21.0,            10.0,    4.0,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',            None,   r'[A-Z\d]\d{7}[A-Z\d]'),
    MS('FR', 'FR', 'France',          20.0,     (10.0,  5.5),   2.1,  None,    'EUR',     'EUR 10000.00',  'EUR 100000.00',  ('EUR 34900.00',
                                                                                                                              'EUR 90300.00'), r'[A-Z\d]{2}\s*\d{9}'),
    MS('HR', 'HR', 'Croatia',         25.0,     (13.0,  5.0),  None,  None,    'HRK',     'HRK 77000.00',  'HRK 270000.00',  'HRK 230000.00',  r'\d{11}'),
    MS('IE', 'IE', 'Ireland',         23.0,     (13.5,  9.0),   4.8,  13.5,    'EUR',     'EUR 41000.00',   'EUR 35000.00',  ('EUR 37500.00',
                                                                                                                              'EUR 75000.00'), r'\d[A-Z\d+*]\d{5}[A-Z]{1,2}'),
    MS('IT', 'IT', 'Italy',           22.0,            10.0,    4.0,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 30000.00',  r'\d{11}'),
    MS('CY', 'CY', 'Cyprus',          19.0,      (9.0,  5.0),  None,  None,    'EUR',     'EUR 10251.00',   'EUR 35000.00',   'EUR 15600.00',  r'\d{8}[A-Z]'),
    MS('LV', 'LV', 'Latvia',          21.0,            12.0,   None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 50000.00',  r'\d{11}'),
    MS('LT', 'LT', 'Lithuania',       21.0,      (9.0,  5.0),  None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 45000.00',  r'\d{9}(?:\d{3})?'),
    MS('LU', 'LU', 'Luxembourg',      15.0,     (12.0,  6.0),   3.0,  12.0,    'EUR',     'EUR 10000.00',  'EUR 100000.00',   'EUR 25000.00',  r'\d{8}'),
    MS('HU', 'HU', 'Hungary',         27.0,     (18.0,  5.0),  None,  None,    'HUF',     'EUR 35000.00',   'EUR 35000.00', 'HUF 6000000.00',  r'\d{8}'),
    MS('MT', 'MT', 'Malta',           18.0,      (7.0,  5.0),  None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',  ('EUR 14000.00',
                                                                                                                              'EUR 24000.00',
                                                                                                                              'EUR 35000.00'), r'\d{8}'),
    MS('NL', 'NL', 'Netherlands',     21.0,             6.0,   None,  None,    'EUR',     'EUR 10000.00',  'EUR 100000.00',            None,   r'\d{9}B\d{2}'),
    MS('AT', 'AT', 'Austria',         20.0,            10.0,   None,  12.0,    'EUR',     'EUR 11000.00',   'EUR 35000.00',   'EUR 30000.00',  r'U\d{8}'),
    MS('PL', 'PL', 'Poland',          23.0,      (8.0,  5.0),  None,  None,    'PLN',     'PLN 50000.00',  'PLN 160000.00',  'PLN 150000.00',  r'\d{10}'),
    MS('PT', 'PT', 'Portugal',        23.0,     (13.0,  6.0),  None,  13.0,    'EUR',     'EUR 10000.00',   'EUR 35000.00',  ('EUR 10000.00',
                                                                                                                              'EUR 12500.00'), r'\d{9}'),
    MS('RO', 'RO', 'Romania',         24.0,      (9.0,  5.0),  None,  None,    'RON',     'RON 34000.00',  'RON 118000.00',  'RON 220000.00',  r'\d{2,10}'),
    MS('SI', 'SI', 'Slovenia',        22.0,             9.5,   None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',   'EUR 50000.00',  r'\d{8}'),
    MS('SK', 'SK', 'Slovakia',        20.0,            10.0,   None,  None,    'EUR',     'EUR 13941.00',   'EUR 35000.00',   'EUR 49790.00',  r'\d{10}'),
    MS('FI', 'FI', 'Finland',         24.0,     (14.0, 10.0),  None,  None,    'EUR',     'EUR 10000.00',   'EUR 35000.00',    'EUR 8500.00',  r'\d{8}'),
    MS('SE', 'SE', 'Sweden',          25.0,     (12.0,  6.0),  None,  None,    'SEK',     'SEK 90000.00',  'SEK 320000.00',            None,   r'\d{12}'),
    MS('GB', 'GB', 'United Kingdom',  20.0,             5.0,   None,  None,    'GBP',     'GBP 81000.00',   'GBP 70000.00',   'GBP 81000.00',  r'\d{3}\s*\d{4}\s*\d{2}(?:\s*\d{3})?|GD\d{3}|HA\d{3}'),
    ]
    
