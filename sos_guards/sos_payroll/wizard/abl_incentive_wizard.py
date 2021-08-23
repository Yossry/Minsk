import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class AblIncentiveWizard(models.TransientModel):
	_name = "abl.incentive.wizard"
	_description = "ABL Incentive Wizard"
		
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payslip.line',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_abl_incentive').with_context(landscape=True).report_action(self, data=datas)
