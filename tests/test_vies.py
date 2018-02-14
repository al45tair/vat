# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import vat
import pytest

# If you add to this list, pick people who:
#
#  (a) Publish their VAT number openly,
#  (b) Won't mind,
#  (c) Will still be around when the next person reads this.
#
# The first three numbers in this list should be from the UK, Spain and
# Germany respectively.  Why?  Because we know that the UK gives out details,
# that Spain doesn't but does fuzzy matching itself, and that Germany is
# broken.
test_numbers = [
    # These are all courtesy of Santander, who publish these details on their
    # various websites (sometimes it takes a moment searching, but they're all
    # public).
    ('GB466264724',
     { 'name': 'Santander UK plc',
        'street': 'Tax Department, B1 / F2 Carlton Park, Narborough',
        'postcode': 'LE19 0AL',
        'city': 'Leicester',
        'state': 'Leicestershire' }),
    ('ESA39000013',
     { 'name': 'Banco Santander, S.A.',
        'city': 'Santander',
        'postcode': '39004' }),
    ('DE120492390',
     { 'name': 'Santander Consumer Bank AG',
       'street': 'Santander-Platz 1',
       'city': 'Mönchengladbach',
       'postcode': '41061' }),
    ('ATU15350108',
     { 'name': 'Santander Consumer Bank GmbH',
       'street': 'Donau-City Straße 6',
       'city': 'Wien',
       'postcode': '1220' }),
    ('DK30733053',
     { 'name': ('Santander Consumer Bank, Filial '
                + 'af Santander Consumer Bank AS, Norge'),
       'street': 'Stamholmen 147 6',
       'city': 'Hvidovre',
       'postcode': '2650' }),
    ('IT05634190010',
     { 'name': 'Santander Consumer Bank Spa',
       'street': 'Via Nizza 262/26',
       'city': 'Torino',
       'postcode': '10126' }),
    ('PL5272046102',
     { 'name': 'Santander Consumer Bank S.A.',
       'street': 'ul. Strzegomska 42c',
       'city': 'Wrocław',
       'postcode': '53-611' }),
    ('PT503811483',
     { 'name': 'Banco Santander Consumer Portugal S.A.',
       'street': 'Rue Castilho, 2',
       'city': 'Lisboa',
       'postcode': '1269-073' }),
    ('SE516406033601',
     { 'name': 'Santander Consumer Bank AS Norge, Sverige Filial',
       'street': 'FE 302',
       'city': 'Stockholm',
       'postcode': '171 75' }),

    # The National Bank of Greece
    ('EL094014201',
     { 'name': 'Τράπεζα της Ελλάδος Α.Ε.',
       'street': 'Αιόλου 86',
       'city': 'Αθήνα',
       'postcode': '10232' }),

    # This one turned out to be awkward
    ('HU13632874',
     { 'name': 'Greenfinity LLC',
       'street': 'Puskin utca 19',
       'city': 'Budapest',
       'state': 'Pest megye',
       'postcode': '1088' }),
]

bad_info = { 'name': 'I am a great big rabbit' }
    
def test_local_fuzzy_vies():
    """Test a VIES response that requires *we* do the fuzzy matching."""
    try:
        valid, response = vat.check_details(test_numbers[0][0],
                                        test_numbers[0][1])
        assert valid == True

        valid, response = vat.check_details(test_numbers[0][0], bad_info)
        assert valid == False
    except vat.VIESHTTPException as e:
        if e.code >= 500 and e.code <= 599:
            pytest.skip('EU VIES server is malfunctioning, so skipping test')
        else:
            raise
        
def test_remote_fuzzy_vies():
    """Test a VIES response where the member state does the fuzzy matching."""
    try:
        valid, response = vat.check_details(test_numbers[1][0],
                                            test_numbers[1][1])
        assert valid == True

        valid, response = vat.check_details(test_numbers[1][0], bad_info)
        assert valid == False
    except vat.VIESHTTPException as e:
        if e.code >= 500 and e.code <= 599:
            pytest.skip('EU VIES server is malfunctioning, so skipping test')
        else:
            raise
        
def test_non_compliant_vies():
    """Test a VIES response where the member state is non-compliant and
    does not provide details *or* do fuzzy matching."""
    try:
        valid, response = vat.check_details(test_numbers[2][0], bad_info)
        assert valid is None
        assert response.trader_info['name'] == bad_info['name']
    except vat.VIESHTTPException as e:
        if e.code >= 500 and e.code <= 599:
            pytest.skip('EU VIES server is malfunctioning, so skipping test')
        else:
            raise
        
def test_all_vies():
    """Test all the numbers we have above, to make sure that we think they
    match."""
    def do_safely(fn):
        try:
            result = fn()
        except vat.VIESHTTPException as e:
            if e.code >= 500 and e.code <= 599:
                pytest.skip('EU VIES server is malfunctioning, so skipping test')
            else:
                raise
        except vat.VIESSOAPException as e:
            if e.string == 'MS_UNAVAILABLE':
                pytest.skip('EU VIES server reports member state unavailable, '
                            'skipping test')
            elif e.string == 'MS_MAX_CONCURRENT_REQ':
                pytest.skip('EU VIES server reports member state capacity '
                            'exceeded, skipping test')
            elif e.string == 'SERVICE_UNAVAILABLE':
                pytest.skip('EU VIES server unavailable, skipping test')
            elif e.string == 'TIMEOUT':
                pytest.skip('EU VIES server timed-out trying to talk to '
                            'member state, skipping test')
            elif e.string == 'SERVER_BUSY':
                pytest.skip('EU VIES server too busy, skipping test')
            else:
                raise
        return result

    for vat_number, details in test_numbers:
        valid, response = do_safely(lambda: vat.check_details(vat_number,
                                                              details))

        if vat_number.startswith('DE'):
            assert valid == None
        else:
            if valid != True:
                print('%s %r' % (vat_number, details))

            assert valid == True

            valid, response = do_safely(lambda: vat.check_details(vat_number,
                                                                  bad_info))

            assert valid == False
