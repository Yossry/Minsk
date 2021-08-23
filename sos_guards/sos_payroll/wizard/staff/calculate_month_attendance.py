import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models
import pdb

class CalculateMonthAttendance(models.TransientModel):
	_name ='calculate.month.attendance'
	_description = 'Calculate Month Attendance'
	
	
	date = fields.Date("Date", required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_from = fields.Date("Date From")
	date_to = fields.Date("Date To")
	total_days = fields.Integer('Month Days',required=True,default=30)
	
	@api.one
	def calculate_attendance(self):
		att_pool = self.env['hr.employee.month.attendance']
		emps = self.env['hr.employee'].search([('status','in',['new','active','onboarding']),('department_id','!=',29),('is_guard','=',False)],order='code')
		fmt = '%YYYY-%MM-%DD'
		
		if emps:		
			for emp in emps:
				atts = self.env['sos.guard.attendance1'].search([('name','>=',self.date_from),('name','<=',self.date_to),('employee_id','=',emp.id)])
				sql = """select count(distinct to_char(name,'%s')) from sos_guard_attendance1 where employee_id = %s and name >= '%s' and name <= '%s' and month_att is Null""" % (fmt,emp.id,str(self.date_from),str(self.date_to))
				self._cr.execute(sql)
				att_count = int(self._cr.fetchall()[0][0])
				if att_count > 0:
					res = {
						'employee_id': emp.id,
						'date': self.date,
						'total_days': self.total_days or 0,
						'present_days': att_count or 0,
						'state': 'draft',
					}								
					att_rec = att_pool.sudo().create(res)
					atts.write({'month_att' : True})
		return {'type': 'ir.actions.act_window_close'}





          
