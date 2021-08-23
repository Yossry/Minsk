import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class GuardSecurityDeposit(models.TransientModel):
	_name = "sos.guards.security.deposit"
	_description = "Security Deposit Wizard"

	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now())[:10])
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payslip.line',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_security_deposit').with_context(landscape=True).report_action(self, data=datas)
