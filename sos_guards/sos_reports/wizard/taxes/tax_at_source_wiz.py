import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_

class TaxAtSourceWiz(models.TransientModel):
	_name = 'tax.at.source.wiz'
	_description = 'Tax At Source Wiz'
		
	date_from = fields.Date("Start Date", default=lambda self: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date("End Date",default=lambda self:str(datetime.now() + relativedelta.relativedelta(day=31))[:10])

	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'account.move.line',
			'form' : data
			}
		return self.env.ref('sos_reports.action_tax_source_report').with_context(landscape=True).report_action(self, data=datas,config=False)