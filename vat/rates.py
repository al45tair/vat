# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from decimal import Decimal as D

from . import vrws
from . import tic

class RateCache (object):
    """Manages a cache of VAT rates fetched from europa.eu's
       VATRateWebService.  Most queries will come from the cache, which will
       only fetch new rates once per day per member state."""
    
    # Historic reduced rates - VRWS currently isn't supplying reduced rate
    # information
    
    # I've tried to pick, as the first entry (with no detail) the most likely
    # rate you'll want.  But you MUST check.  Also, as of 1st Sept 2015, NONE
    # of this information is available via the web service, so the detail may
    # change to something else.
    historic_reduced_rates = {
        'BE': (D('6.0'), (D('12.0'), 'Alternate'), (D('12.0'), 'Parking')),
        'BG': (D('9.0'),),
        'CZ': (D('15.0'), (D('10.0'), 'Alternate')),
        'DK': None,
        'DE': (D('7.0'),),
        'EE': (D('9.0'),),
        'EL': (D('13.0'), (D('6.0'), 'Alternate')),
        'ES': (D('10.0'), (D('4.0'), 'Super Reduced')),
        'FR': (D('5.5'), (D('10.0'), 'Alternate'), (D('2.1'), 'Super Reduced')),
        'HR': (D('5.0'), (D('13.0'), 'Alternate')),
        'IE': (D('13.5'), (D('9.0'), 'Alternate'), (D('4.8'), 'Super Reduced'),
               (D('13.5'), 'Parking')),
        'IT': (D('10.0'), (D('4.0'), 'Super Reduced')),
        'CY': (D('5.0'), (D('9.0'), 'Alternate')),
        'LV': (D('12.0'),),
        'LT': (D('9.0'), (D('5.0'), 'Alternate')),
        'LU': (D('8.0'), (D('3.0'), 'Super Reduced'), (D('14.0'), 'Parking')),
        'HU': (D('5.0'), (D('18.0'), 'Alternate')),
        'MT': (D('5.0'), (D('7.0'), 'Alternate')),
        'NL': (D('6.0'),),
        'AT': (D('10.0'), (D('12.0'), 'Parking')),
        'PL': (D('8.0'), (D('5.0'), 'Alternate')),
        'PT': (D('6.0'), (D('13.0'), 'Alternate'), (D('13.0'), 'Parking')),
        'RO': (D('9.0'), (D('5.0'), 'Alternate')),
        'SI': (D('9.5'),),
        'SK': (D('10.0'),),
        'FI': (D('10.0'), (D('14.0'), 'Alternate')),
        'SE': (D('6.0'), (D('12.0'), 'Alternate')),
        'GB': (D('5.0'),),
        }
        
    def __init__(self):
        self.rates = {}

    def _get_rates(self, member_state):
        if not isinstance(member_state, basestring):
            member_state = member_state.code
        today = datetime.date.today()
        rinfo = self.rates.get(member_state, None)
        if rinfo is not None:
            if rinfo[1] == today:
                return rinfo[0]
        try:
            rates = vrws.get_rates(member_state, date=today)
        except vrws.VRWSException:
            rates = tic.get_rates(member_state, date=today)

        self.rates[member_state] = (rates, today)
        return rates

    def regions(self, member_state):
        """Retrieve a list of regions for the given member state."""
        rates = self._get_rates(member_state)
        return rates.regions.keys()

    def _best_rate(self, rates):
        today = datetime.date.today()
        rate_date = None
        best_rate = None
        for rate in rates:
            if rate.application_date > today or rate.detail is not None:
                continue
            if rate_date is None or rate.application_date > rate_date:
                best_rate = rate
        return best_rate
    
    def standard_rates(self, member_state, region=None):
        """Retrieve the set of standard rates for the given member state,
        optionally for the specified region.

        N.B.: This method returns a LIST of rates, and you should use the
        date and detail information to find the appropriate one.  There may
        be multiple rates with different application dates, *and* there may
        be rates with detail specifications in the list."""
        rates = self._get_rates(member_state)
        if region is not None:
            rates = rates.regions[region]
        return rates.types.get(vrws.STANDARD, [])

    def standard_rate(self, member_state, region=None):
        """Return today’s ordinary standard rate for the given member state
        and (optional) region."""
        return self._best_rate(self.standard_rates(member_state, region))

    def _to_rate(self, rate_info, the_date):
        if isinstance(rate_info, tuple):
            return vrws.Rate(rate_info[0], the_date, rate_info[1])
        else:
            return vrws.Rate(rate_info, the_date, None)
    
    def reduced_rates(self, member_state, region=None):
        """Retrieve the set of reduced rates for the given member state,
        optionally for the specified region.

        N.B.: This method returns a LIST of rates, and you should use the
        date and detail information to find the appropriate one.  There may
        be multiple rates with different application dates, *and* there may
        be rates with detail specifications in the list.

        N.B. 2: As of 1st September 2015, most member states are not providing
        reduced rate information via the web service.  If we find that a
        member state has not provided the necessary information, we fall back
        to a built-in table."""
        rates = self._get_rates(member_state)
        if region is not None:
            rates = rates.regions[region]
        rates = rates.types.get(vrws.REDUCED, None)
        if rates is None:
            rates = self.historic_reduced_rates.get(member_state, None)
            if rates is None:
                return []
            the_date = datetime.date(2015,9,1)
            rates = [self._to_rate(r, the_date) for r in rates]
        return rates
    
    def reduced_rate(self, member_state, region=None):
        """Return today’s ordinary reduced rate for the given member state
        and (optional) region."""
        return self._best_rate(self.reduced_rates(member_state, region))
    
    def category_rates(self, member_state, category, region=None):
        """Retrieve the set of rates for the given member state, category
        and (optional) region.

        N.B.: This method returns a LIST of rates, and you should use the
        date and detail information to find the appropriate one.  There may
        be multiple rates with different application dates, *and* there may
        be rates with detail specifications in the list."""
        rates = self._get_rates(member_state)
        if region is not None:
            rates = rates.regions[region]
        return rates.categories.get(category, [])
    
    def category_rate(self, member_state, category, region=None):
        """Return today’s rate for the given member state, category and
        (optional) region."""
        return self._best_rate(self.category_rates(member_state,
                                                   category,
                                                   region))
    
    def categories(self, member_state, region=None):
        """Return a list of categories for the given member state and
        (optional) region."""
        rates = self._get_rates(member_state)
        if region is not None:
            rates = rates.regions[region]
        return rates.categories.keys()
