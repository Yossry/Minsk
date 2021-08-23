import time
import pdb
from odoo import api, fields, models

class SOSGuardsDailyAttendanceWizard(models.TransientModel):
	_name = "guards.daily.attendance.wizard"
	_description = "Guards Daily Attendance Report"
	
	date_to = fields.Date("Date To",default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', 'Projects')

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'guards_daily_attendance_report_aeroo',
			'datas': datas,
		}
