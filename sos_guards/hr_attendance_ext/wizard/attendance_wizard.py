import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AttendanceWizard(models.TransientModel):
	_name = 'attendance.wizard'
	_description = 'Attendance Wizard'	
	
	@api.model
	def _get_employee_ids(self):
		emp_ids = self.env['hr.employee'].browse(self._context.get('active_ids',False))
		return emp_ids and emp_ids.ids or []
	
	date = fields.Date('Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1))[:10])
	employee_ids = fields.Many2many('hr.employee','att_emp_rel2', 'att_id2', 'emp_id2', string='Employee(s)', default=_get_employee_ids)
		
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
		return self.env.ref('hr_attendance_ext.action_report_employee_attendance').report_action(employees, data=datas, config=False)
	
