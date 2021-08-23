from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
from io import StringIO,BytesIO
import io
import pdb

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

## Date Methods
def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()
	
def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
	

class LeaveReportWizard(models.TransientModel):
	_name = 'leaves.report.wizard'
	_description = 'Leaves Report Wizard'	
	
	date_from = fields.Date('From Date (Request)', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-5))[:10])
	date_to = fields.Date('To Date (Request)', required=True,default=lambda *a: str(datetime.now())[:10])
	company_id = fields.Many2one('res.company', 'Company',required=True,default=lambda self: self.env.user.company_id.id)
	
	
	@api.multi
	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Salary Sheet")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		worksheet.write_merge(0, 1, 0, 9,"Employee Leaves Report", style = style_title)
		
		row = 3
		col = 0
        		  
		table_header = ['Sr#','EMP#','Name','Department','Request Date','Leave Type','Start Date','End Date','Days','Leave Status']
		for i in range(10):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		holidays = self.env['hr.leave'].search([('create_date','>=',self.date_from),('create_date','<=',self.date_to),('state','!=','refuse')],order='employee_id, create_date')
		
		sr = 1
		for holiday in holidays:
			row += 1
			col = 0  
			worksheet.write(row,col, sr)
			col +=1
			worksheet.write(row,col, holiday.employee_id.code)
			col +=1
			worksheet.write(row,col, holiday.employee_id.english_name)
			col +=1
			worksheet.write(row,col, holiday.employee_id.department_id.name)
			col +=1
			if holiday.create_date:
				request_date = strToDatetime(holiday.create_date)
				request_date_str = datetime.strftime(request_date,'%d-%m-%Y')
				worksheet.write(row,col, request_date_str)
			col +=1
			
			worksheet.write(row,col, holiday.holiday_status_id.name)
			col +=1
			
			if holiday.date_from:
				date_from = strToDate(holiday.date_from)
				date_from_str = datetime.strftime(date_from,'%d-%m-%Y')
				worksheet.write(row,col, date_from_str)
			else:
				worksheet.write(row,col, '-')	
			col +=1
			
			if holiday.date_to:
				date_to = strToDate(holiday.date_to)
				date_to_str = datetime.strftime(date_to,'%d-%m-%Y')
				worksheet.write(row,col, date_to_str)
			else:
				worksheet.write(row,col, '-')
			col +=1
			
			worksheet.write(row,col, holiday.number_of_days_temp)
			col +=1
			
			if holiday.state == 'validate':
				worksheet.write(row,col, 'Approved')
			if not holiday.state == 'validate' and holiday.pending_approver:
				approver = holiday.pending_approver
				if approver:
					sts = approver.category_ids[0].name
					sts = "Pending With " + sts	
					worksheet.write(row,col, sts)
			sr += 1
	 
		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['leaves.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Leaves Report.xls'
		})
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Leaves Report Save Form',
			'res_model': 'leaves.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}
		

class leaves_report_save_wizard(models.TransientModel):
    _name = "leaves.report.save.wizard"
    _description = "Save Wizard for the Leaves Report"
    
    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)		
				

