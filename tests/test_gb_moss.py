# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import vat
import io
from vat.gb import moss

def test_empty_moss():
    """Test generating an empty MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f)

        assert f.getvalue() != b''

def test_uk_moss():
    """Test generating a UK-only MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, uk_supplies = [
            ('FR', moss.STANDARD_RATE, 12.34, 123.45),
            ('DE', moss.REDUCED_RATE, 56.78, 12345.678)
            ])

        assert f.getvalue() != b''

def test_fe_moss():
    """Test generating a foreign establishment MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, fe_supplies = [
            ('DE1234567', 'FR', moss.STANDARD_RATE, 12.345, 678.901)
            ])

        assert f.getvalue() != b''

def test_uk_fe_moss():
    """Test generating a UK & FE MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, uk_supplies = [
            ('FR', moss.STANDARD_RATE, 12.34, 123.45),
            ('DE', moss.REDUCED_RATE, 56.78, 12345.678)
            ],
            fe_supplies = [
            ('DE1234567', 'FR', moss.STANDARD_RATE, 12.345, 678.901)
            ])

        assert f.getvalue() != b''
