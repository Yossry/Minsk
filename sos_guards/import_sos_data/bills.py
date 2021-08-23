# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _


import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io
import pdb

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class gen_bills(models.TransientModel):
	_name = "gen.bills"
	_description = 'Generate Mobile Bills'

	file = fields.Binary('File')
	sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option',default='custom')
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')

	@api.multi
	def make_bill_date(self, date):
		DATETIME_FORMAT = "%Y-%m-%d"
		i_date = datetime.strptime(date, DATETIME_FORMAT)
		return i_date
	
	@api.multi
	def make_bills(self,values):
		bill_obj = self.env['sos.sim.bills']
		bill_date = self.make_bill_date(values.get('bill_date'))
		bill_id = bill_obj.create({
			'name' : values.get('name'),
			'bill_month' : values.get('bill_month'),
			'sim_number': values.get('sim_number'),
			'bill_date': bill_date,
			'inv_amount': values.get('inv_amount'),
			'state' : 'draft',
		})
		return bill_id


	@api.multi
	def import_bills(self):
		"""Load data from the CSV file."""
		if self.import_option == 'csv':        
			keys = ['order', 'customer', 'pricelist','product', 'quantity', 'uom', 'description', 'price','user','tax','date']
			data = base64.b64decode(self.file)
			file_input = io.StringIO(data.decode("utf-8"))
			file_input.seek(0)
			reader_info = []
			reader = csv.reader(file_input, delimiter=',')

			try:
				reader_info.extend(reader)
			except Exception:
				raise exceptions.Warning(_("Not a valid file!"))
			values = {}
			for i in range(len(reader_info)):
				#val = {}
				field = list(map(str, reader_info[i]))
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						values.update({'option':self.import_option,'seq_opt':self.sequence_opt})
						res = self.make_sale(values)
		else:             
			fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
			fp.write(binascii.a2b_base64(self.file))
			fp.seek(0)
			values = {}
			workbook = xlrd.open_workbook(fp.name)
			sheet = workbook.sheet_by_index(0)
			prev_order = False
			
			for row_no in range(sheet.nrows):
				val = {}
				if row_no <= 0:
					fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
				else:
					#line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
					line = list(map(lambda row:str(row.value), sheet.row(row_no)))
					a1 = int(float(line[3]))
					a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
					date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
				
					values.update({
						'name': line[0],
						'bill_month': line[1],
						'sim_number': line[2],
						'bill_date':date_string,
						'inv_amount': line[4],								
						'seq_opt':self.sequence_opt,
					})				
					prev_order = self.make_bills(values)                            
		return prev_order

