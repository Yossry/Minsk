import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GuardsBankAccount(models.TransientModel):
	_name = "guards.bank.account"
	_description = "Guards Bank Account Wizard"

	project_ids = fields.Many2many('sos.project', string='Filter on Projects')
	center_ids = fields.Many2many('sos.center', string='Filter on Centers')
	
	@api.multi
	def print_report(self):
		
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos.report_guards_bankaccount').with_context(landscape=True).report_action(self, data=datas)
