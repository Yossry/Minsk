import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _


class complaints_statistics_project(models.TransientModel):
	_name = 'complaints.statistics.project'
	_description = 'Complaints Statistics Project'
	
	start_date = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	end_date = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now())[:10])

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.project',
			'form' : data
		}
		return self.env.ref('sos_complaint.report_complaint_statistics').with_context(landscape=True).report_action(self, data=datas)
