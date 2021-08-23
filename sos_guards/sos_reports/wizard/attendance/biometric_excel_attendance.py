import time
import pdb
from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone, utc
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT, DEFAULT_SERVER_DATETIME_FORMAT


import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

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


class BiometricExcelAttendance(models.TransientModel):
	_name = "biometric.excel.attendance"
	_description = "BioMetric Excel Attendance Report"

	start_date = fields.Date("Date From", required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	end_date = fields.Date("Date To",required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
	segment_ids = fields.Many2many('hr.segmentation',string="Segments")
	sub_segment_ids = fields.Many2many('hr.sub.segmentation',string="Sub Segments")
	employee_ids = fields.Many2many('hr.employee', string='Filter on Employee', help="""Only selected Employee will be printed. Leave empty to print all Employee.""")
	department_ids = fields.Many2many('hr.department', string='Filter on Department', help="""Only selected Department will be printed. Leave empty to print all Department.""")                           		

	
	#***** Excel Report *****#
	@api.multi
	def make_excel(self):
		#***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Attendance Report")
		
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_date_col = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_date_col2 = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")
		style_product_header = xlwt.easyxf("font:height 200; font: name Liberation Sans,bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		style_table_totals2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		new_style = xlwt.easyxf('align: horiz left; borders: left thin, right thin, top thin, bottom thin;')
		
		#col width
		col_1 = worksheet.col(0)
		col_1.width = 256 * 8
		col_2 = worksheet.col(1)
		col_2.width = 256 * 10
		col_3 = worksheet.col(2)
		col_3.width = 256 * 40
		col_4 = worksheet.col(3)
		col_4.width = 256 * 20
		col_5 = worksheet.col(4)
		col_5.width = 256 * 20
		col_6 = worksheet.col(5)
		col_6.width = 256 * 20
		col_7 = worksheet.col(6)
		col_7.width = 256 * 20
		col_8 = worksheet.col(7)
		col_8.width = 256 * 40
		col_9 = worksheet.col(8)
		col_9.width = 256 * 20
		
		worksheet.write_merge(0, 1, 0, 8,"Excel Attendance Report", style = style_title)
		row = 2
		col = 0
		
		#***** Table Heading *****#
		table_header = ['Sr#','Enroll Number','Employee Name','Attendnce Date','Attendnce Time','Center','Post','Device Name','Verify Mode']
		for i in range(9):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
		domain = [('department_id','!=',29),]
		employees = False
		if self.project_ids:
			domain.append(('project_id','in',self.project_ids.ids),)
		if  self.center_ids:
			domain.append(('center_id','in',self.center_ids.ids),)
		if  self.segment_ids:
			domain.append(('segment_id','in',self.segment_ids.ids),)	
		if  self.sub_segment_ids:
			domain.append(('sub_segment_id','in',self.sub_segment_ids.ids),)
		if  self.department_ids:
			domain.append(('department_id','in',self.department_ids.ids),)
		
		if self.employee_ids:
			employees = self.env['hr.employee'].search([('id','in',self.employee_ids.ids)])
		if not self.employee_ids:
			employees = self.env['hr.employee'].search(domain)				
		
		if employees:
			attendances = self.env['sos.guard.attendance1'].search([('name','>=',self.start_date),('name','<=',self.end_date),('employee_id','in',employees.ids)], order='employee_id,name')	
			i =1
			
			for att in attendances:
				row += 1
				col = 0
				
				dt = datetime.strptime(str(att.name),"%Y-%m-%d %H:%M:%S")
				dt = dt + relativedelta.relativedelta(hours=5)
				dtAtt = datetime.strftime(dt,'%d-%m-%Y %H:%M:%S')
				
				worksheet.write(row,col,i, style=style_date_col)
				col +=1
				worksheet.write(row,col,att.employee_id.code, style=style_date_col)
				col +=1
				worksheet.write(row,col,att.employee_id.name, style=style_date_col)
				col +=1
				worksheet.write(row,col,dtAtt[:10], style=style_date_col)
				col +=1
				worksheet.write(row,col,dtAtt[11:], style=style_date_col)
				col +=1
				worksheet.write(row,col,att.center_id and att.center_id.name or '', style=style_date_col)
				col +=1
				worksheet.write(row,col,att.post_id and att.post_id.name or '', style=style_date_col)
				col +=1
				worksheet.write(row,col,att.device_id and att.device_id.name or '', style=style_date_col)
				col +=1
				worksheet.write(row,col,att.action, style=style_date_col)
				col +=1
				
				i +=1 

		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Attendance.xls'
		})
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Excel Attendance',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}