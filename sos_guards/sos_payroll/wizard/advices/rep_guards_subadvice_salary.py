import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class guards_subadvice_salary(models.TransientModel):
	_name ='guards.subadvice.salary'
	_description = 'Guards Subadvice Report'

	advice_id = fields.Many2one('guards.payroll.advice', 'Payment Advice')
	acc = fields.Many2one('guards.payroll.advice.line', 'Advice Line')
	acc2 = fields.Char('Account No.', size=32)
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payroll.advice',
			'form' : data
		}
		return self.env.ref('sos_payroll.action_guards_subadvice_salary_report').with_context(landscape=False).report_action(self, data=datas)

