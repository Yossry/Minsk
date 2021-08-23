import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class PostsAttendanceRegisterWizard(models.TransientModel):
	_name = "posts.attendance.register.wizard"
	_description = "Posts Attendance Register Report"
			
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])
	center_id = fields.Many2one('sos.center', 'Center')
	project_id = fields.Many2one('sos.project', 'Project')

	
	

	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.guard.attendance',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_posts_attendance_register').with_context(landscape=True).report_action(self, data=datas)
