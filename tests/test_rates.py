# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import vat
import pytest
from vat.rates import RateCache


@pytest.mark.parametrize('member_state', vat.member_states)
def test_rate_cache_standard_rate(member_state):
    cache = RateCache()
    rate = cache.standard_rate(member_state.code)
    assert rate is not None
