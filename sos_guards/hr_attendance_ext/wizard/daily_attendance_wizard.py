import time
import pdb
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class DailyAttendanceWizard(models.TransientModel):
	_name = 'daily.attendance.wizard'
	_description = 'Daily Attendance'
	
	@api.model
	def _get_employee_ids(self):
		emp_ids = self.env['hr.employee'].browse(self._context.get('active_ids',False))
		return emp_ids and emp_ids.ids or []
	
	start_date = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	end_date = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now())[:10])
	employee_ids = fields.Many2many('hr.employee','att_emp_rel', 'att_id', 'emp_id', string='Employee(s)', default=_get_employee_ids)
	page_breaker = fields.Boolean("Page Breaker", default=False)
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data] = self.read()
		if not data.get('employee_ids'):
			raise UserError(_('You have to select at least one Employee. And try again.'))
		employees = self.env['hr.employee'].browse(data['employee_ids'])
		datas = {
			'ids': [],
			'model': 'hr.attendance',
			'form': data
		}
		return self.env.ref('hr_attendance_ext.action_report_daily_attendance').report_action(employees, data=datas, config=False)
		
