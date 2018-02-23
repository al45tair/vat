# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import vat
import pytest
from vat import vrws


def test_vrws():
    try:
        for ms in vat.member_states:
            rates = vrws.get_rates(ms.code)
            assert isinstance(rates, vrws.Rates)
            assert len(rates.types[vrws.STANDARD]) > 0
    except vat.VRWSHTTPException as e:
        if e.code >= 500 and e.code <= 599:
            pytest.skip('EU VRWS server is malfunctioning, so skipping test')
        else:
            raise
