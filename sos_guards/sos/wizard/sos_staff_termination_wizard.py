import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class sos_staff_termination_wizard(models.TransientModel):
	_name = 'sos.staff.termination.wizard'
	_description = 'Staff Termination Wizard'
	
	
	@api.model
	def _get_staff_id(self):
		employee_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
		if employee_id:
			return employee_id.id
		return True	
		
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True,readonly=True,default=_get_staff_id)
	termination_date = fields.Date('Termination Date', required=True, default=lambda *a: str(datetime.now())[:10])
	join_termination = fields.Selection([('rejoin','Re-Join'),('terminate','Terminate')], default='terminate')
	
	@api.one
	def staff_termination(self):
		# 98 = HR Manager
		# 97 = HR Officer
		# 42 = HR Master
		# 25 = Adviser
		flag = False
		access_ids = [25,42,97,98]
		group_ids = self.env.user.groups_id.ids or False
		resource_id = self.employee_id.resource_id.id
		
		if group_ids:
			for access_id in access_ids:
				if access_id in group_ids:
					flag = True


		#Termination Process
		if flag and self.join_termination == 'terminate' and self.employee_id.department_id.id !=29:
			if self.employee_id.status == 'terminated':
				self.employee_id.resigdate = self.termination_date
				self.employee_id.current = False
				
			elif self.employee_id.status in ['new','open','onboarding','active']:
				self.employee_id.status = 'terminated'
				self.employee_id.resigdate = self.termination_date
				self.employee_id.current = False
				contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')])
				if contracts:
					for contract in contracts:
						contract.date_end = self.termination_date
						#contract.state = 'done'
						contract.state = 'close'
						
				#self.employee_id.active = False 
				self.env.cr.execute("update resource_resource set active=False where id =%s"%(resource_id))									
			else:
				raise UserError(_('Employee State is not in open New, Open and OnBoarding!'))
		
		#Rejoin Process
		elif flag and self.join_termination == 'rejoin' and self.employee_id.department_id.id !=29:
			self.employee_id.appointmentdate = self.termination_date
			self.employee_id.resigdate = False
			self.employee_id.status = 'active'
			self.employee_id.current = True
			#self.employee_id.active = True
			self.env.cr.execute("update resource_resource set active=True where id =%s"%(resource_id))									
			
		else:
			raise UserError(_('You are not Authorized to do this!'))	
						
		return {'type': 'ir.actions.act_window_close'}	 
	
