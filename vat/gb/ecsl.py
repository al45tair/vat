from xml.sax import saxutils

B2B_GOODS = 0
B2B_INTERMEDIARY = 2
B2B_SERVICES = 3

def generate(file_obj,
             vat_number, branch, year, period, contact, lines):
    """Generate an HMRC XML ECSL document.

       :param file_obj: A file-like object to which the ECSL should be written.
       :param str vat_number: The numeric part of your UK VAT number.
       :param int branch: The branch number (set to 0 if you don't know
         otherwise).
       :param int year: The year.
       :param int period: The month within the year (if quarterly, it should be
         the month at the end of the current quarter).
       :param str contact: The name of the contact for HMRC.
       :param lines: An iterable yielding (country, VAT number, value, type)
         tuples.  The country is a two-character EU VAT country code; the VAT
         number must be unadorned and numeric; the value should be an integer in
         Sterling, and may be negative.  The type field should be one of

           vat.gb.ecsl.B2B_GOODS
           vat.gb.ecsl.B2B_INTERMEDIARY
           vat.gb.ecsl.B2B_SERVICES
        """

    file_obj.write(("""<?xml version="1.0" encoding="UTF-8"?>
<Submission type='HMRC_VAT_ESL_BULK_SUBMISSION_FILE'>
  <TraderVRN>%(vat_number)s</TraderVRN>
  <Branch>%(branch)03d</Branch>
  <Year>%(year)04d</Year>
  <Period>%(period)02d</Period>
  <CurrencyA3>GBP</CurrencyA3>
  <ContactName>%(contact)s</ContactName>
  <Online>0</Online>
  <SubmissionLines>
""" % { 'vat_number': vat_number,
        'branch': branch,
        'year': year,
        'period': period,
        'contact': saxutils.escape(contact) }).encode('utf-8'))

    for country, vat_number, value, kind in lines:
        file_obj.write(("""    <SubmissionLine>
      <CountryA2>%(country)s</CountryA2>
      <CustomerVRN>%(vat_number)s</CustomerVRN>
      <Value>%(value)d</Value>
      <Indicator>%(kind)d</Indicator>
    </SubmissionLine>
""" % { 'country': country,
        'vat_number': vat_number,
        'value': value,
        'kind': kind }).encode('utf-8'))

    file_obj.write(b"""  </SubmissionLines>
</Submission>
""")
