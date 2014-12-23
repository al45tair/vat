# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import vies, addresscmp

def check_details(vat_number, vat_info={}, requester=None, address_threshold=0.7):
    """Check a VAT number using VIES.  Unlike the functions in vat.vies, this
    deals with the fact that different member states may behave in different
    ways, and will always try to do a reasonable job.

    The ``vat_info`` dictionary should contain entries for 'name',
    'street', 'postcode', and 'city'.  It can also contain an entry for
    'state', though that won't be sent to VIES (since VIES doesn't support it).

    This function returns a tuple (match, VIESApproxResponse), where ``match``
    is True, False or None, which means that we weren't able to determine
    automatically whether or not the details match, but the VAT number itself
    is OK."""

    vat_number = vat_number.upper()
    
    response = vies.check_vat_approx(vat_number, vat_info, requester)

    if not response.valid:
        return (False, response)
    
    # Some member states do fuzzy matching and return these properties,
    # but not all do, so we have to (a) check if they have and
    # (b) check if they're just ignoring everything and not actually
    # checking.
    ms_fuzzy = False
    ms_processed = False
    for m in [ 'name', 'company-type', 'street', 'postcode', 'city' ]:
        status = response.trader_match_info.get(m, '')
        if status:
            ms_fuzzy = True

        if status != vies.MATCH_NOT_PROCESSED:
            ms_processed = True

        if status == vies.MATCH_INVALID:
            return (False, response)

    # Ignore member states if they don't actually check anything
    if ms_fuzzy and not ms_processed:
        ms_fuzzy = False

    if not ms_fuzzy:
        if vat_number.startswith('DE'):
            # Germany IS ANNOYING!
            # The Germans are not doing fuzzy matching *AND* they are also
            # not returning data (they just pass it straight back unchanged).
            # This is against EU law, but what do they care?
            vies_address = ''
        else:
            # Member states that don't do fuzzy matching, are *supposed* to
            # return the trader's address so that we can do it ourselves.
            vies_address = response.trader_info.get('address', '')
            if not vies_address:
                vies_address = []
                for m in [ 'name', 'street', 'postcode', 'city' ]:
                    item = response.trader_info.get(m, '')
                    if item:
                        vies_address.append(item)
                vies_address = ' '.join(vies_address)

        if not vies_address:
            return (None, response)

        user_address = []
        for item in ['street', 'postcode', 'city', 'state']:
            info = vat_info.get(item, None)
            if info:
                user_address.append(info)
        user_address = ' '.join(user_address)

        score = addresscmp.compare(vies_address, user_address)
        if score < address_threshold:
            return (False, response)

    return (True, response)
