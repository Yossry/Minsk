from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import re
import csv
from io import StringIO,BytesIO
import io
import pdb

import logging
_logger = logging.getLogger(__name__)

from io import StringIO

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
	
	
class exit_form_salary_advice_rep(models.TransientModel):
	_name = 'exit.form.salary.advice.rep'
	_description = 'Exit Form Payroll Advice'
	
	@api.model
	def _get_advice_id(self):
		adv_id = self.env['guards.payroll.advice'].browse(self._context.get('active_id',False))
		if adv_id:
			return adv_id.id
		return True	
	
	##Cols
	advice_id = fields.Many2one('guards.payroll.advice', "Advice", required=True,default=_get_advice_id)
	
	
	def remove_dashes(self,name):
		return re.sub('-','',name)	

	@api.multi
	def get_salary_advice(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet('0')
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_rows = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		
		table_header = ['SR#','ERP No.','Name','CNIC','Account Number','Salary Amount','Security Amount','Net Amount']
		row = 0
		col = 0
		
		for i in range(8):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1	
		
		i = 1
		for line in self.advice_id.line_ids:
			net_amt = self.env['guards.payslip.line'].search([('slip_id','=',line.slip_id.id),('code', '=', 'NET')]).total or 0
			security_amt = self.env['guards.payslip.line'].search([('slip_id','=',line.slip_id.id),('code', '=', 'GSDR')]).total or 0
			net = (net_amt - security_amt)
			row += 1
			col =0
			
			worksheet.write(row,col,i,style=style_table_rows)
			col +=1
			worksheet.write(row,col,line.employee_id.code,style=style_table_rows)
			col +=1
			worksheet.write(row,col,line.employee_id.name,style=style_table_rows)
			col +=1
			worksheet.write(row,col,line.employee_id.cnic,style=style_table_rows)
			col +=1
			worksheet.write(row,col,line.acctitle,style=style_table_rows)
			col +=1
			worksheet.write(row,col,net,style=style_table_rows)
			col +=1
			worksheet.write(row,col,security_amt,style=style_table_rows)
			col +=1
			worksheet.write(row,col,(round(line.bysal)),style=style_table_rows)
			col +=1
			i +=1
			
		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Exit Form Advice (XLS).xls'
		})
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Exit Form Advice (XLS)',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}
		
