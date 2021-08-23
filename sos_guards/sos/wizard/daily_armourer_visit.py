import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _

class daily_armourer_visit(models.TransientModel):

	_name = 'daily.armourer.visit'
	_description = 'Daily Armourer Visit Report'
	
	date_from = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_end = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now())[:10])
	

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.armourer.visit',
			'form' : data
		}
		return self.env.ref('sos.report_armourer_visit').with_context(landscape=True).report_action(self, data=datas)
