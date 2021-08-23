import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class sos_staff_attendance_wizard(models.TransientModel):
	_name = 'sos.staff.attendance.wizard'
	_description = 'Staff Attendance'
	
	
	#@api.onchange('date')
	#def compute_employee(self):
	#	employee_ids = []
	#	emps = self.env['hr.employee'].search([('status','in',['new','active','onboarding']),('department_id','!=',29),('is_guard','=',False)],order='department_id,code')
	#	if emps:
	#		employee_ids = emps.ids
	#		self.staff_ids = [(6,0,employee_ids)]	
		
	date = fields.Date('Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1,day=1))[:10])
	total_days = fields.Integer('Month Days',required=True,default=30)
	present_days = fields.Integer('Present Days',required=True,default=30)
	staff_ids = fields.Many2many('hr.employee', string='Employee')
	
	@api.one
	def staff_attendance(self):
		att_obj = self.env['hr.employee.month.attendance']
		# 94 = HR Director
		# 25 = Adviser
		
		flag = False
		access_ids = [25,94]
		group_ids = self.env.user.groups_id.ids or False
		
		if group_ids:
			for access_id in access_ids:
				if access_id in group_ids:
					flag = True
					
		if flag:
			if self.staff_ids:
				for emp in self.staff_ids:
					
					### Checking Already Attendance of employee for this month ###
					if att_obj.search([('employee_id','=',emp.id),('date','>=',self.date),('date','<=',self.date)]):
						continue
						
					else:	
						res = {
								'date' : self.date,
								'total_days' : self.total_days,
								'present_days' : self.present_days,
								'employee_id' : emp.id,
								'state' : 'draft',
							}
						att_obj.create(res)	
		else:
			raise UserError(_('You are not Authorized to do this!'))			
		return {'type': 'ir.actions.act_window_close'}	 
	
