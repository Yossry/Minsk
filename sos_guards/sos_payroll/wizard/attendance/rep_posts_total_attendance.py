import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class PostsTotalAttendance(models.TransientModel):
	_name = "sos.posts.total.attendance"
	_description = "Posts Total Attendance Wizard"
			
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now())[:10])
	center_id = fields.Many2one('sos.center','Center')
	project_id = fields.Many2one('sos.project','Project')
	

	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_posts_total_attendance').with_context(landscape=True).report_action(self, data=datas)
