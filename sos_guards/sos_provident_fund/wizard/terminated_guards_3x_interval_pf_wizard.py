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


class TerminatedGuards3XIntervalPFWizard(models.TransientModel):
	_name = "terminated.guards.3x.interval.pf.wizard"
	_description = "Terminated Guards 3X Interval PF"

	interval = fields.Integer('Interval', default=3)

	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_provident_fund.action_terminated_guards_3x_interval_pf_report').with_context(landscape=True).report_action(self, data=datas)

	# ***** Excel Report *****#
	@api.multi
	def make_excel(self):
		# ***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Terminated Guards 3x Interval PF Report")

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

		worksheet.write_merge(0, 1, 0, 9, "Terminated Guards (3x interval) PF Report", style=style_title)
		row = 2
		col = 0

		# ***** Table Heading *****#
		row = 2
		col = 0
		table_header = ['Sr#', '3x Employee', '3 Month', '6x Employee', '6 Month', '9x Employee', '9 Month', '12x Employee','12 Month', 'Total']
		for i in range(10):
			worksheet.write(row, col, table_header[i], style=style_table_header)
			col += 1

		##DATA Handling From PDF Report
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'hr.employee',
			'form': data
		}
		result = self.env['report.sos_provident_fund.terminated_guards_3x_pf_report']._get_report_values(self,data=datas)
		if result['rep_data']:
			i = 1
			for ln in result['rep_data']:
				row += 1
				col = 0
				worksheet.write(row, col, i, style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['3x_emp'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['3x'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['6x_emp'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['6x'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['9x_emp'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['9x'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['12x_emp'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['12x'], style=style_date_col)
				col += 1
				worksheet.write(row, col, ln['total'], style=style_date_col)
				col += 1
				i +=1



		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['sos.advice.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Terminated Guards (3x Interval) PF Report.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Terminated Guards (3x Interval) PF Report',
			'res_model': 'sos.advice.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}