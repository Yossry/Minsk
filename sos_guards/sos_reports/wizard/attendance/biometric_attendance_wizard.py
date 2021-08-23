import time
import pdb
from odoo import api, fields, models, _


class BiometricAttendanceWizard(models.TransientModel):
	_name = "biometric.attendance.wizard"
	_description = "BioMetric Attendance Report"
	
	to_day = fields.Date("Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	rep = fields.Selection( [('staff','Staff Report'),('guard','Guards Report')],"Report",default="staff")
	
	employee_ids = fields.Many2many('hr.employee', string='Filter on Employee', help="""Only selected Employee will be printed. Leave empty to print all Employee.""")
	department_ids = fields.Many2many('hr.department', string='Filter on Department', help="""Only selected Department will be printed. Leave empty to print all Department.""")                           		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
		
	@api.multi
	def print_report(self):		
		##Certains things are ignored just for Staff is doning
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'sos.guard.attendance1',
			'form': data
		}
		return self.env.ref('sos_reports.action_report_biometric_attendance_summary').with_context(landscape=True).report_action(self, data=datas, config=False)