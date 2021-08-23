import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class GuardsNoContractWizard(models.TransientModel):
	_name = "guards.no.contract.wizard"
	_description = "Guards No Contract Wizard"
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_guards_no_contract').with_context(landscape=True).report_action(self, data=datas)
