import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models
import pdb

class guards_payslip_lines_contribution_register(models.TransientModel):
	_name = 'guards.payslip.lines.contribution.register'
	_description = 'PaySlip Lines by Contribution Registers'
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	register_id = fields.Many2one('hr.contribution.register', 'Contribution Register')

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.contribution.register',
			'form' : data
		}
		return self.env.ref('sos_payroll.guards_payslip_contribution_register').with_context(landscape=True).report_action(self, data=datas)


	