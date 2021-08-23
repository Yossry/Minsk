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
	
class sos_guards_salary_advice_rep(models.TransientModel):
	_name = 'sos.guards.salary.advice.rep'
	_description = 'Salary Advice'
	
	@api.model
	def _get_advice_id(self):
		adv_id = self.env['guards.payroll.advice'].browse(self._context.get('active_id',False))
		if adv_id:
			return adv_id.id
		return True
	
	#Cols	
	advice_id = fields.Many2one('guards.payroll.advice', "Advice", required=True,default=_get_advice_id)
	
	
	def remove_dashes(self,name):
		return re.sub('-','',name)	

	@api.multi
	def get_salary_advice(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet('0')
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_rows = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		
		col_0 = worksheet.col(0)
		col_0.width = 256 * 40
		col_1 = worksheet.col(1)
		col_1.width = 256 * 10
		col_2 = worksheet.col(2)
		col_2.width = 256 * 10
		
		table_header = ['Account','Amount','D/C']
		row = 0
		col = 0
		
		for i in range(3):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
			
		for line in self.advice_id.line_ids:
			row += 1
			col =0
			
			worksheet.write(row,col,self.remove_dashes(line.name),style=style_table_rows)
			col +=1
			worksheet.write(row,col,round(line.bysal),style=style_table_rows)
			col +=1
			worksheet.write(row,col,line.debit_credit,style=style_table_rows)
			col +=1
			
		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Salary Advice.xls'
		})
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Salary Advice (XLS)',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}
		


class sos_advice_report_save_wizard(models.TransientModel):
    _name = "sos.advice.report.save.wizard"
    _description = 'Additional Wizard for Different Excel or CSV Reports'
    
    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)		
				
			
			
