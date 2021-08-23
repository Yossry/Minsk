
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError

## This Wizard is being used to stop (to write the stop in the bank name of the guards) who has ##
## Been terminated During that salary Period But their Clearnce is not Sure ##

class SalaryStopWizard(models.TransientModel):
	_name = "salary.stop.wizard"
	_description = "Salary Stop Wizard"
	
	
	@api.model
	def _get_payslips(self):
		res = False
		if self._context.get('active_model', False) == 'guards.payslip' and self._context.get('active_ids', False):
			res = self._context['active_ids']
		return res
	
	#Cols		
	slip_ids = fields.Many2many('guards.payslip', string='Guard Payslips', default=_get_payslips)
	
	#Function
	@api.multi
	def salary_stop_funct(self):
		for slip in self.slip_ids:
			body = "Bank Name is Changed TO the STOP By the User " + self.env.user.name
			slip.bank_temp_id = slip.bank and slip.bank.id or False
			slip.bank = 35		## 35 Stop
			slip.message_post(body=body)
	
	#Function
	@api.multi
	def salary_restore_funct(self):
		for slip in self.slip_ids:
			body = "Bank Name is Restored To Previous By the User " + self.env.user.name
			if slip.bank_temp_id:
				slip.bank = slip.bank_temp_id and slip.bank_temp_id.id
				slip.message_post(body=body)
