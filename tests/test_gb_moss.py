# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import vat
import io
from vat.gb import moss

def test_empty_moss():
    """Test generating an empty MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f)

        with open('/tmp/empty.ods', 'wb') as f2:
            f2.write(f.getvalue())
            
        assert f.getvalue() != b''

def test_uk_moss():
    """Test generating a UK-only MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, uk_supplies = [
            ('FR', moss.STANDARD_RATE, 12.34, 123.45, 8.88),
            ('DE', moss.REDUCED_RATE, 56.78, 12345.678, 99.9)
            ])

        with open('/tmp/uk.ods', 'wb') as f2:
            f2.write(f.getvalue())
            
        assert f.getvalue() != b''

def test_fe_moss():
    """Test generating a foreign establishment MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, fe_supplies = [
            ('DE1234567', 'FR', moss.STANDARD_RATE, 12.345, 678.901, 23.45)
            ])

        with open('/tmp/fe.ods', 'wb') as f2:
            f2.write(f.getvalue())
            
        assert f.getvalue() != b''

def test_uk_fe_moss():
    """Test generating a UK & FE MOSS return."""
    with io.BytesIO() as f:
        moss.generate(f, uk_supplies = [
            ('FR', moss.STANDARD_RATE, 12.34, 123.45, 8.88),
            ('DE', moss.REDUCED_RATE, 56.78, 12345.678, 99.9)
            ],
            fe_supplies = [
            ('DE1234567', 'FR', moss.STANDARD_RATE, 12.345, 678.901, 23.45)
            ])

        with open('/tmp/uk_fe.ods', 'wb') as f2:
            f2.write(f.getvalue())
            
        assert f.getvalue() != b''
