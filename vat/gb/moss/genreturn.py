import zipfile
import pkg_resources
import datetime
import io
import re
import decimal
import bisect
import copy
from lxml import etree

from ... import MemberState

STANDARD_RATE = 'Standard'
REDUCED_RATE = 'Reduced'

TABLE = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'
TEXT = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'

def v(obj):
    wrapper = etree.Element(TEXT + 'p')
    wrapper.text = '%s' % obj
    return wrapper

class RepeatArray(object):
    def __init__(self):
        self.index = []
        self.items = []

    def copy_item(self, item):
        return copy.deepcopy(item)

    def set_repeat(self, item, repeat):
        pass
    
    def insert_before(self, item, new_item):
        pass

    def insert_after(self, item, new_item):
        pass

    def before_split(self):
        pass

    def after_split(self):
        pass
    
    def get(self, ndx, split=False):
        rndx = bisect.bisect_left(self.index, ndx, 0, len(self.index) - 2)
        item = self.items[rndx]
        if split:
            repeat = self.index[rndx + 1] - self.index[rndx]
            if repeat != 1:
                self.before_split()
                andx = self.index[rndx]
                before = andx - ndx
                after = self.index[rndx + 1] - ndx - 1
                self.set_repeat(item, 1)
                if before:
                    item_before = self.copy_item(item)
                    self.set_repeat(item_before, before)
                    self.items.insert(rndx, item_before)
                    rndx += 1
                    self.index.insert(rndx, ndx)
                    self.insert_before(item, item_before)
                if after:
                    item_after = self.copy_item(item)
                    self.set_repeat(item_after, after)
                    self.items.insert(rndx + 1, item_after)
                    self.index.insert(rndx + 1, ndx + 1)
                    self.insert_after(item, item_after)
                self.after_split()
        return item
    
class Row(RepeatArray):
    def __init__(self, row):
        super(Row, self).__init__()
        self.row = row

        colndx = 1
        for col in row.iterfind(TABLE + 'table-cell'):
            self.index.append(colndx)
            self.items.append(col)
            repeat = col.get(TABLE + 'number-columns-repeated')
            if repeat:
                colndx += int(repeat)
            else:
                colndx += 1
        self.index.append(colndx)

    def set_repeat(self, column, repeat):
        if repeat == 1:
            try:
                del column.attrib[TABLE + 'number-columns-repeated']
            except KeyError:
                pass
        else:
            column.set(TABLE + 'number-columns-repeated', '%s' % repeat)

    def insert_before(self, column, new_column):
        ndx = self.row.index(column)
        self.row.insert(ndx, new_column)

    def insert_after(self, column, new_column):
        ndx = self.row.index(column)
        self.row.insert(ndx + 1, new_column)

_ref_re = re.compile(r'([A-Z]+)([0-9]+)')
class Sheet(RepeatArray):
    def __init__(self, table):
        super(Sheet, self).__init__()
        self.table = table
        
        rowndx = 1
        for row in table.iterfind(TABLE + 'table-row'):
            self.index.append(rowndx)
            self.items.append(row)
            repeat = row.get(TABLE + 'number-rows-repeated')
            if repeat:
                rowndx += int(repeat)
            else:
                rowndx += 1
        self.index.append(rowndx)

    def set_repeat(self, row, repeat):
        if repeat == 1:
            try:
                del row.attrib[TABLE + 'number-rows-repeated']
            except KeyError:
                pass
        else:
            row.set(TABLE + 'number-rows-repeated', '%s' % repeat)

    def insert_before(self, row, new_row):
        ndx = self.table.index(row)
        self.table.insert(ndx, new_row)

    def insert_after(self, row, new_row):
        ndx = self.table.index(row)
        self.table.insert(ndx + 1, new_row)
        
    def cell(self, cell):
        m = _ref_re.match(cell.upper())
        row = int(m.group(2))
        col_a = m.group(1)
        col = 0
        for ch in col_a:
            chval = ord(ch) - ord('A') + 1
            col = 26 * col + chval
        return Row(self.get(row, split=True)).get(col, split=True)

def table(content, name):
    return content.find('.//{table}table[@{table}name="{name}"]'.format(table=TABLE, name=name))

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
       :param uk_supplies: An iterable yielding (MSC, rate type, rate, net value,
         vat due) tuples.  The MSC should be a two-character EU VAT country code
         or a MemberState object; the rate type should be one of

           :py:const:`STANDARD_RATE`
           :py:const:`REDUCED_RATE`

         The net value should be the value in Sterling.
       :param fe_supplies: An iterable yielding (VAT number, MSC, rate
         type, rate, net value, vat due) tuples.  The VAT number should
         include the two-character EU VAT country code; the MSC should be a
         two-character EU VAT country code or a MemberState object; the rate
         type should be one of

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
                                                    'resources/return-template.ods')
      
    with zipfile.ZipFile(template_stream, 'r') as template:
        with zipfile.ZipFile(file_obj, 'w') as output:
            # Copy everything apart from the worksheet pages (which we find
            # and parse)
            for item in template.infolist():
                data = template.read(item)
                if item.filename == 'content.xml':
                    content = etree.fromstring(data)
                    content_info = item
                    uk_sheet = Sheet(table(content, 'UK_SUPPLIES'))
                    fe_sheet = Sheet(table(content,
                                           'FIXED_ESTABLISHMENT_SUPPLIES'))
                else:
                    output.writestr(item, data)

            # Build the Quarter field
            quarter = 'Q%s/%s' % (quarter, year)

            # Set up for two dp
            two_dp = decimal.Decimal('.01')
            
            # Fill-in the UK supplies worksheet
            e10 = uk_sheet.cell('E10')
            e10[:] = [v(quarter)]

            made_supplies = False
            for ndx,supply in enumerate(uk_supplies):
                msc,rate_type,rate,net_value,vat_due = supply

                if ndx == 150:
                    raise TooManySupplies()
                
                if not isinstance(msc, MemberState):
                    msc = MemberState.by_code(msc)

                row_ndx = ndx + 17

                msc_cell = uk_sheet.cell('D%s' % row_ndx)
                msc_cell[:] = [v(msc.name)]
                rtype_cell = uk_sheet.cell('E%s' % row_ndx)
                rtype_cell[:] = [v(rate_type)]
                rate_cell = uk_sheet.cell('F%s' % row_ndx)
                rate_cell[:] = [v(decimal.Decimal(rate).quantize(two_dp))]
                net_cell = uk_sheet.cell('G%s' % row_ndx)
                net_cell[:] = [v(decimal.Decimal(net_value).quantize(two_dp))]
                vat_cell = uk_sheet.cell('H%s' % row_ndx)
                vat_cell[:] = [v(decimal.Decimal(vat_due).quantize(two_dp))]
                made_supplies = True

            if made_supplies:
                made_supplies = 'Yes'
            else:
                made_supplies = 'No'
                
            e12 = uk_sheet.cell('E12')
            e12[:] = [v(made_supplies)]
            
            # Fill-in the fixed establishment worksheet
            e11 = fe_sheet.cell('E11')
            e11[:] = [v(quarter)]

            made_supplies = False
            for ndx,supply in enumerate(fe_supplies):
                vat_number,msc,rate_type,rate,net_value,vat_due = supply

                if ndx == 150:
                    raise TooManySupplies()
                
                if not isinstance(msc, MemberState):
                    msc = MemberState.by_code(msc)

                row_ndx = ndx + 18

                vn_cell = fe_sheet.cell('D%s' % row_ndx)
                vn_cell[:] = [v(vat_number)]
                msc_cell = fe_sheet.cell('E%s' % row_ndx)
                msc_cell[:] = [v(msc.name)]
                rtype_cell = fe_sheet.cell('F%s' % row_ndx)
                rtype_cell[:] = [v(rate_type)]
                rate_cell = fe_sheet.cell('G%s' % row_ndx)
                rate_cell[:] = [v(decimal.Decimal(rate).quantize(two_dp))]
                net_cell = fe_sheet.cell('H%s' % row_ndx)
                net_cell[:] = [v(decimal.Decimal(net_value).quantize(two_dp))]
                vat_cell = fe_sheet.cell('I%s' % row_ndx)
                vat_cell[:] = [v(decimal.Decimal(vat_due).quantize(two_dp))]
                made_supplies = True

            if made_supplies:
                made_supplies = 'Yes'
            else:
                made_supplies = 'No'
                
            e13 = fe_sheet.cell('E13')
            e13[:] = [v(made_supplies)]

            # Write the worksheets
            output.writestr(content_info,
                            etree.tostring(content, encoding='utf8'))
