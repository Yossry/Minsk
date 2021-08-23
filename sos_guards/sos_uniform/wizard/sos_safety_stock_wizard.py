import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class SOSSafetyStockWizard(models.TransientModel):
	"""Will launch Safety Stock report Wizard"""
	_name = "sos.safety.stock.wizard"
	_description = "Safety Stock All Report"
	
	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.safety.demand',
			'form' : data
		}
		return self.env.ref('sos_uniform.report_safety_stock').with_context(landscape=True).report_action(self, data=datas)
