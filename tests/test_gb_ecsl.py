# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io

from vat.gb import ecsl

def test_empty_ecsl():
    """Test generation of an empty EC sales list."""
    output = io.BytesIO()

    ecsl.generate(output, '123456789', 0, 2014, 3, 'A N Other', [])

    assert output.getvalue() == b"""<?xml version="1.0" encoding="UTF-8"?>
<Submission type='HMRC_VAT_ESL_BULK_SUBMISSION_FILE'>
  <TraderVRN>123456789</TraderVRN>
  <Branch>000</Branch>
  <Year>2014</Year>
  <Period>03</Period>
  <CurrencyA3>GBP</CurrencyA3>
  <ContactName>A N Other</ContactName>
  <Online>0</Online>
  <SubmissionLines>
  </SubmissionLines>
</Submission>
"""

def test_simple_ecsl():
    """Test generation of a simple EC sales list."""
    output = io.BytesIO()

    ecsl.generate(output, '123456789', 0, 2014, 3, 'A N Other',
                  [ ('HU', '12345678', 19, ecsl.B2B_SERVICES),
                    ('NL', '87654321B01', -28, ecsl.B2B_GOODS),
                    ('PT', '123456789', 44, ecsl.B2B_INTERMEDIARY) ])

    assert output.getvalue() == b"""<?xml version="1.0" encoding="UTF-8"?>
<Submission type='HMRC_VAT_ESL_BULK_SUBMISSION_FILE'>
  <TraderVRN>123456789</TraderVRN>
  <Branch>000</Branch>
  <Year>2014</Year>
  <Period>03</Period>
  <CurrencyA3>GBP</CurrencyA3>
  <ContactName>A N Other</ContactName>
  <Online>0</Online>
  <SubmissionLines>
    <SubmissionLine>
      <CountryA2>HU</CountryA2>
      <CustomerVRN>12345678</CustomerVRN>
      <Value>19</Value>
      <Indicator>3</Indicator>
    </SubmissionLine>
    <SubmissionLine>
      <CountryA2>NL</CountryA2>
      <CustomerVRN>87654321B01</CustomerVRN>
      <Value>-28</Value>
      <Indicator>0</Indicator>
    </SubmissionLine>
    <SubmissionLine>
      <CountryA2>PT</CountryA2>
      <CustomerVRN>123456789</CustomerVRN>
      <Value>44</Value>
      <Indicator>2</Indicator>
    </SubmissionLine>
  </SubmissionLines>
</Submission>
"""

def test_utf8_ecsl():
    """Test that we can use unusual characters in the contact name."""

    output = io.BytesIO()

    ecsl.generate(output, '123456789', 0, 2014, 3, 'Ж؈ဆあ & <>', [])

    assert output.getvalue().decode('utf-8') == \
"""<?xml version="1.0" encoding="UTF-8"?>
<Submission type='HMRC_VAT_ESL_BULK_SUBMISSION_FILE'>
  <TraderVRN>123456789</TraderVRN>
  <Branch>000</Branch>
  <Year>2014</Year>
  <Period>03</Period>
  <CurrencyA3>GBP</CurrencyA3>
  <ContactName>Ж؈ဆあ &amp; &lt;&gt;</ContactName>
  <Online>0</Online>
  <SubmissionLines>
  </SubmissionLines>
</Submission>
"""
