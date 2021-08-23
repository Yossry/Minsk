import time
import pdb
from odoo import api, fields, models, _

class ReportGuardAttendanceWizard(models.TransientModel):
	_name = "guards.attendance.wizard"
	_description = "Guards Attendance Report"
	
	date_from = fields.Date("Date From",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("Date To",default=lambda *a: time.strftime('%Y-%m-%d'))
	group_by = fields.Selection([('guards','Guards'),('posts','Posts')],'Group By',default='posts')
		
	employee_ids = fields.Many2many('hr.employee', string='Filter on Guards', help="""Only selected Guards will be printed. Leave empty to print all Guards.""")
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")                           		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          

		
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.guard.attendance',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_guard_attendance').with_context(landscape=True).report_action(self, data=datas,config=False)
