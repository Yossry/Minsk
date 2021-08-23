import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


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


class BiometricAttendanceSummaryWizard(models.TransientModel):
	_name = "biometric.attendance.summary.wizard"
	_description = "BioMetric Attendance Report"
	
	start_date = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	end_date = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])	
	employee_ids = fields.Many2many('hr.employee', string='Filter on Employee', help="""Only selected Employee will be printed. Leave empty to print all Employee.""")
	department_ids = fields.Many2many('hr.department', string='Filter on Department', help="""Only selected Department will be printed. Leave empty to print all Department.""")                           		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
	generate_month_entries = fields.Boolean('Generate Month Entres', defaul=False)
	
	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'sos.guard.attendance1',
			'form': data
		}

		return self.env.ref('sos_reports.action_report_biometric_attendance_summary').with_context(landscape=True).report_action(self, data=datas, config=False)

	# ***** Excel Report *****#
	@api.multi
	def make_excel(self):
		# ***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("BioMetric Summary Attendance")

		style_title = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header2 = xlwt.easyxf("font:height 170; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern:")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_date_col = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_date_col2 = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")
		style_product_header = xlwt.easyxf("font:height 200; font: name Liberation Sans,bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		style_table_totals2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		new_style = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")

		##DATA Handling From PDF Report
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'sos.guard.attendance1',
			'form': data
		}
		result = self.env['report.sos_reports.report_biometric_attendancesummary']._get_report_values(self, data=datas)
		get_day = result['get_day']
		rep_data = result['get_data_from_report']
		days_length = len(result['get_day'])
		loop_val = days_length + 9 + 2 - 1
		heading = "BioMetric Attendance Summary Report From " + str(self.start_date) + " To " + str(self.end_date)

		# col width
		for i in range(2, loop_val+1):
			col_i= worksheet.col(i)
			col_i.width = 256 * 6

		#Sheet Headers
		worksheet.write_merge(0, 1, 0, loop_val, heading, style=style_title)
		row = 2
		col = 0

		# ***** Table Heading *****#
		worksheet.write_merge(row, row + 1, 0, 1, "Employees ERP ID", style=new_style)
		col = 2

		for i in range(days_length): #-1 Because range starts 0
			worksheet.write(row, col, get_day[i]['day_str'], style=style_table_header)
			col += 1
		worksheet.write_merge(row, row, col, col + 8, "Summary", style=style_title)

		row = 3
		col = 2
		for i in range(days_length):
			worksheet.write(row, col, get_day[i]['day'], style=style_table_header)
			col += 1

		summary_header = ["M", "P", "LT", "SL", "HL", "L", "LW", "A", "T"]
		for i in range(9):
			worksheet.write(row, col, summary_header[i], style=style_table_header)
			col += 1

		row = 4
		col = 0
		for rec in rep_data:
			for rec_data in rec['data']:
				col = 0
				worksheet.write_merge(row, row, 0, 1, rec_data['emp'], style=style_table_header)
				col = 2
				for rec_datail in rec_data['display']:
					worksheet.write(row, col,rec_datail['In'], style=style_table_header2)
					col +=1
				worksheet.write(row, col, rec_data['summary'][0]['M'] and rec_data['summary'][0]['M'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['P'] and rec_data['summary'][0]['P'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['LT'] and rec_data['summary'][0]['LT'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['S'] and rec_data['summary'][0]['S'] or '',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['H'] and rec_data['summary'][0]['H'] or '',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['L'] and rec_data['summary'][0]['L'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['W'] and rec_data['summary'][0]['W'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['A'] and rec_data['summary'][0]['A'] or '-',style=style_table_header2)
				col += 1
				worksheet.write(row, col, rec_data['summary'][0]['T'] and rec_data['summary'][0]['T'] or '-',style=style_table_header2)
				col += 1
				row += 1


		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Bio Metric Attendance Summary.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Bio Metric Attendance Summary',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}