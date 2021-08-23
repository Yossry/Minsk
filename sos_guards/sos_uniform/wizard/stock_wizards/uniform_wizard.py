import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class UniformWizard(models.TransientModel):
	_name = "uniform.wizard"
	_description = "Uniform Wizard"
	
	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))		
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'uniform.wizard',
			'form' : data
		}
		return self.env.ref('sos_uniform.uniform_report').with_context(landscape=True).report_action(self, data=datas)
