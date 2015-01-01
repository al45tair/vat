import zipfile
import pkg_resources
import datetime
import io
import re
import decimal
from lxml import etree

from ... import MemberState

STANDARD_RATE = 'Standard'
REDUCED_RATE = 'Reduced'

def v(v):
    wrapper = etree.Element('v')
    wrapper.text = '%s' % v
    return wrapper

_ref_re = re.compile(r'([A-Z]+)([0-9]+)')
def cell(sheet, ref):
    m = _ref_re.match(ref.upper())
    return sheet.find('./{*}sheetData/{*}row[@r="%s"]/{*}c[@r="%s"]'
                      % (m.group(2), m.group(0)))

class TooManySupplies(Exception):
    """Raised if you attempt to generate a MOSS return with more than 150
    supplies."""
    pass

def generate(file_obj,
             quarter=None, year=None,
             uk_supplies=[],
             fe_supplies=[]):
    """Generate an HMRC VAT MOSS return document.

       :param file_obj: A file-like object to which the VAT MOSS return should
         be written.
       :param int quarter: The quarter (1, 2, 3 or 4) for this return.
         Defaults to the previous quarter.
       :param int year: The year (e.g. 2015) for this return.
         Defaults to the current year.
       :param uk_supplies: An iterable yielding (MSC, rate type, rate, net value)
         tuples.  The MSC should be a two-character EU VAT country code or a
         MemberState object; the rate type should be one of

           :py:const:`STANDARD_RATE`
           :py:const:`REDUCED_RATE`

         The net value should be the value in Sterling.
       :param fe_supplies: An iterable yielding (VAT number, MSC, rate
         type, rate, net value) tuples.  The VAT number should include the
         two-character EU VAT country code; the MSC should be a two-character
         EU VAT country code or a MemberState object; the rate type should be
         one of

           :py:const:`STANDARD_RATE`
           :py:const:`REDUCED_RATE`

         The net value should be the value in Sterling.
        """

    today = datetime.date.today()
    
    if year is None:
        year = today.year

    if quarter is None:
        quarter = ((today.month - 4) // 3) % 4 + 1

    template_stream = pkg_resources.resource_stream('vat.gb.moss',
                                                    'resources/return-template.xlsx')
      
    with zipfile.ZipFile(template_stream, 'r') as template:
        with zipfile.ZipFile(file_obj, 'w') as output:
            # Copy everything apart from the worksheet pages (which we find
            # and parse)
            for item in template.infolist():
                data = template.read(item)
                if item.filename == 'xl/worksheets/sheet1.xml':
                    # This is the UK supplies worksheet
                    uk_sheet = etree.fromstring(data)
                    uk_info = item
                elif item.filename == 'xl/worksheets/sheet2.xml':
                    # This is the Fixed Establishment supplies worksheet
                    fe_sheet = etree.fromstring(data)
                    fe_info = item
                elif item.filename == 'xl/sharedStrings.xml':
                    # This is the shared strings file
                    sst = etree.fromstring(data)
                    sst_index = dict()
                    
                    for ndx,si in enumerate(sst.findall('./{*}si')):
                        key = etree.tostring(si)
                        sst_index[key] = ndx
                        
                    class SSTProps (object):
                        pass
                    sst_props = SSTProps()
                    sst_props.count = int(sst.attrib['count'])
                    sst_props.unique = int(sst.attrib['uniqueCount'])
                    sst_info = item
                else:
                    output.writestr(item, data)

            def s(s):
                t_elt = etree.Element('t')
                t_elt.text = s
                si_elt = etree.Element('si')
                si_elt.append(t_elt)

                key = etree.tostring(si_elt)

                sid = sst_index.get(key, None)

                if sid is None:
                    sst.append(si_elt)
                    sid = sst_props.unique
                    sst_index[key] = sid
                    sst_props.unique += 1
                    
                sst_props.count += 1
                
                return sid

            # Build the Quarter field
            quarter = s('Q%s/%s' % (quarter, year))

            # Set up for two dp
            two_dp = decimal.Decimal('.01')
            
            # Fill-in the UK supplies worksheet
            e10 = cell(uk_sheet, 'E10')
            e10.attrib['t'] = 's'
            e10[:] = [v(quarter)]

            made_supplies = False
            for ndx,supply in enumerate(uk_supplies):
                msc,rate_type,rate,net_value = supply

                if ndx == 150:
                    raise TooManySupplies()
                
                if not isinstance(msc, MemberState):
                    msc = MemberState.by_code(msc)

                row_ndx = ndx + 17
                row = uk_sheet.find('./{*}sheetData/{*}row[@r="%s"]' % row_ndx)
                msc_cell = row.find('./{*}c[@r="D%s"]' % row_ndx)
                msc_cell.attrib['t'] = 's'
                msc_cell[:] = [v(s(msc.name))]
                rtype_cell = row.find('./{*}c[@r="E%s"]' % row_ndx)
                rtype_cell.attrib['t'] = 's'
                rtype_cell[:] = [v(s(rate_type))]
                rate_cell = row.find('./{*}c[@r="F%s"]' % row_ndx)
                rate_cell[:] = [v(decimal.Decimal(rate).quantize(two_dp))]
                net_cell = row.find('./{*}c[@r="G%s"]' % row_ndx)
                net_cell[:] = [v(decimal.Decimal(net_value).quantize(two_dp))]
                made_supplies = True

            if made_supplies:
                made_supplies = s('Yes')
            else:
                made_supplies = s('No')
                
            e12 = cell(uk_sheet, 'E12')
            e12.attrib['t'] = 's'
            e12[:] = [v(made_supplies)]
            
            # Fill-in the fixed establishment worksheet
            e11 = cell(fe_sheet, 'E11')
            e11.attrib['t'] = 's'
            e11[:] = [v(quarter)]

            made_supplies = False
            for ndx,supply in enumerate(fe_supplies):
                vat_number,msc,rate_type,rate,net_value = supply

                if ndx == 150:
                    raise TooManySupplies()
                
                if not isinstance(msc, MemberState):
                    msc = MemberState.by_code(msc)

                row_ndx = ndx + 18
                row = fe_sheet.find('./{*}sheetData/{*}row[@r="%s"]' % row_ndx)
                vn_cell = row.find('./{*}c[@r="D%s"]' % row_ndx)
                vn_cell.attrib['t'] = 's'
                vn_cell[:] = [v(s(vat_number))]
                msc_cell = row.find('./{*}c[@r="E%s"]' % row_ndx)
                msc_cell.attrib['t'] = 's'
                msc_cell[:] = [v(s(msc.name))]
                rtype_cell = row.find('./{*}c[@r="F%s"]' % row_ndx)
                rtype_cell.attrib['t'] = 's'
                rtype_cell[:] = [v(s(rate_type))]
                rate_cell = row.find('./{*}c[@r="G%s"]' % row_ndx)
                rate_cell[:] = [v(decimal.Decimal(rate).quantize(two_dp))]
                net_cell = row.find('./{*}c[@r="H%s"]' % row_ndx)
                net_cell[:] = [v(decimal.Decimal(net_value).quantize(two_dp))]
                made_supplies = True              

            if made_supplies:
                made_supplies = s('Yes')
            else:
                made_supplies = s('No')
                
            e13 = cell(fe_sheet, 'E13')
            e13.attrib['t'] = 's'
            e13[:] = [v(made_supplies)]

            # Write the shared string table
            sst.attrib['count'] = str(sst_props.count)
            sst.attrib['uniqueCount'] = str(sst_props.unique)
            output.writestr(sst_info, etree.tostring(sst, encoding='utf8'))
            
            # Write the worksheets
            output.writestr(uk_info, etree.tostring(uk_sheet, encoding='utf8'))
            output.writestr(fe_info, etree.tostring(fe_sheet, encoding='utf8'))
