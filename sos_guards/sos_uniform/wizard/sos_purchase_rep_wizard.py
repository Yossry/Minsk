import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class SOSPurchaseReportWizard(models.TransientModel):
	"""Will launch Purchase report Wizard"""
	_name = "sos.purchase.report.wizard"
	_description = "Purchase Report"

	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	categ_id = fields.Many2one('product.category', 'Category', required = True)

	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'stock.move',
			'form' : data
		}
		return self.env.ref('sos_uniform.report_purchase_main').with_context(landscape=True).report_action(self, data=datas)
