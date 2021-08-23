import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import api, fields, models

STATE2NAME = {
	'draft': 'Draft',
	'open': 'Open',
	'review': 'Review',
	'approve': 'Approve',
	'dispatch': 'Dispatch',
	'done': 'Delivered',	
	'dispatch_deliver': 'Dispatched & Delivered',
	'none_dispatched': 'Non Dispatched',
	'all': 'Except Draft',
	'reject': 'Reject',
	'cancel': 'Cancel',
}


class UniformReportWizard(models.TransientModel):
	_name = "uniform.report.wizard"
	_description = "Uniform Report Wizard"
	
	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	center_id = fields.Many2one('sos.center', 'Center')
	project_id = fields.Many2one('sos.project', 'Projects')
	state = fields.Selection([('draft','Draft'),('open','Open'),('review','Review'),('approve','Approve'),('dispatch','Dispatch'),('done','Delivered'),('dispatch_deliver','Dispatched & Delivered'),('none_dispatched','Non Dispatched'),('all','Except Draft'),('reject','Reject'),('cancel','Cancel'),], string='Status',default='dispatch_deliver')
	report_name = fields.Selection([('uniform_report_aeroo','Uniform Report'),('uniform_center_all_aeroo','Center Over All'),('uniform_center_specific_aeroo','Specific Center'),('uniform_project_all_aeroo','Project Over All'),('uniform_project_specific_aeroo','Specific Project'),('uniform_post_all_aeroo','Posts Summary'),('uniform_post_specific_aeroo','Specific Post')],'Report',default='uniform_report_aeroo')
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'uniform.report.wizard',
			'form' : data
		}
		report_name =  data['report_name']
		
		if report_name == 'uniform_report_aeroo':
			rep = 'sos_uniform.report_uniform_main'
		
		if report_name == 'uniform_center_all_aeroo':
			rep = 'sos_uniform.report_uniform_center_all'
			
		if report_name == 'uniform_center_specific_aeroo':
			rep = 'sos_uniform.report_uniform_center_specific'
			
		if report_name == 'uniform_project_all_aeroo':
			rep = 'sos_uniform.report_uniform_project_all'
			
		if report_name == 'uniform_project_specific_aeroo':
			rep = 'sos_uniform.report_uniform_project_specific'	
			
		if report_name == 'uniform_post_all_aeroo':
			rep = 'sos_uniform.report_uniform_post_all'
			
		if report_name == 'uniform_post_specific_aeroo':
			rep = 'sos_uniform.report_uniform_post_specific'

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas)