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
from openerp.exceptions import UserError, ValidationError
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
    

class sos_accounts_updation(models.TransientModel):
	_name = "sos.accounts.updation"
	_description = 'SOS Accounts Updatation Through Excel File'

	file = fields.Binary('File')
	sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option',default='custom')
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')

	@api.multi
	def make_accounts_date(self, date):
		DATETIME_FORMAT = "%Y-%m-%d"
		i_date = datetime.strptime(date, DATETIME_FORMAT)
		return i_date
	
	
	@api.multi
	def update_account_info(self):
		"""Load data from the CSV file."""
		if self.import_option == 'csv':        
			keys = ['reference', 'bank_id', 'bankacctitle','bankacc']
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
					line = list(map(lambda row:str(row.value), sheet.row(row_no)))
					#line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
					#a1 = int(float(line[3]))
					#a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
					#date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
					
					erp_id = line[0]
					vals = line[0].split('.')
					if vals:
						erp_id = vals[0]
					
					emp_ref = self.env['hr.employee'].search([('code','=', erp_id)])
					bank_id = self.env['sos.bank'].search([('name','=',line[1])], order="id", limit=1)
					
					acc_value = line[4] or False
					if acc_value:
						acc_owner = ''
						if acc_value == 'Self':
							acc_owner = 'selff'
						elif acc_value == 'Accountant':
							acc_owner = 'acc'
						elif acc_value == 'Regional Manager':
							acc_owner = 'rm'
						elif acc_value == 'Supervisor':
							acc_owner = 'sp'
						elif acc_value == 'Other':
							acc_owner = 'other'
						else:
							acc_owner = ''					
							
					if emp_ref and bank_id:
						values.update({
							'bank_id': bank_id and bank_id.id or '',
							'bankacctitle': line[2],
							'bankacc': line[3],
							'accowner': acc_owner,
						})
						
						emp_ref.write(values)
					else:
						raise UserError(_('Whether Guard Code or Bank is not Found.File Shows the ERP ID: %s') % (line[0]))

