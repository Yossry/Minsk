import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class ComplaintsSummary(models.TransientModel):
	_name = 'complaints.summary'
	_description = 'Complaints Summary Report'

	start_date = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1))[:10])
	end_date = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now())[:10])     
	order_by = fields.Selection([('name','Number'),('center_id','Center'),('project_id','Project'),('complaint_time','Complaint Time'),('coordinator_id','Coordinator')],'Order By',default='center_id')
		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Complaints of selected Projects will be printed. Leave empty to print all Projects.""")                             
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Complaints of selected Centers will be printed. Leave empty to print all Centers.""")                          
	coordinator_ids = fields.Many2many('hr.employee',string='Coordinator', domain=[('is_guard','=',False)], help="""Complaints regarding selected Coordinators will be printed. Leave empty to print all Coordinators.""")
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Closed')],'Status',help="""Complaints of selected Status will be printed. Leave empty to print all.""")

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.complaint',
			'form' : data
		}
		return self.env.ref('sos_complaint.report_complaint_summary').with_context(landscape=True).report_action(self, data=datas)
