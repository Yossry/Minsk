import pdb
from odoo import api, fields, models

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


class MonthWisePFWizard(models.TransientModel):
	_name = "month.wise.pf.wizard"
	_description = "Month Wise PF Wizard"


	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_provident_fund.action_month_wise_pf_report').with_context(landscape=True).report_action(self, data=datas)

	#***** Excel Report *****#
	@api.multi
	def make_excel(self):
		# ***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Month Wise PF Report")

		style_title = xlwt.easyxf(
			"font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf(
			"font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_totals = xlwt.easyxf(
			"font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_date_col = xlwt.easyxf(
			"font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_date_col2 = xlwt.easyxf(
			"font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")

		worksheet.write_merge(0, 1, 0,13, "Month Wise PF Report", style=style_title)
		row = 2
		col = 0

		# ***** Table Heading *****#
		row = 2
		col = 0
		table_header = ['Sr#', 'January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September','October','November','December','Total']
		for i in range(14):
			worksheet.write(row, col, table_header[i], style=style_table_header)
			col += 1

		##DATA Handling From PDF Report
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'hr.employee',
			'form': data
		}
		result = self.env['report.sos_provident_fund.month_wise_pf_report']._get_report_values(self,data=datas)
		if result['rep_data']:
			i = 1
			for ln in result['rep_data']:
				row += 1
				col = 0
				worksheet.write(row, col, i, style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['jan'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['feb'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['mar'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['apr'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['may'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['jun'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['jul'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['aug'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['sep'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['oct'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['nov'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['dec'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['total'], style=style_date_col)
				col += 1
				i +=1


		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Month Wise PF Report.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Month Wise PF Report',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}