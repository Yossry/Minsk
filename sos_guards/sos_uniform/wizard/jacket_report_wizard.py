import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class JacketReportWizard(models.TransientModel):
	_name = "jacket.report.wizard"
	_description = "Jackets Report Wizard"
	
	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	center_id = fields.Many2one('sos.center', 'Center')
	project_id = fields.Many2one('sos.project', 'Projects')
	report_name = fields.Selection([('jacket_report_aeroo','Jacket Report'),('jacket_center_all_aeroo','Center Over All'),('jacket_center_specific_aeroo','Specific Center'),('jacket_project_all_aeroo','Project Over All'),('jacket_project_specific_aeroo','Specific Project'),('jacket_post_all_aeroo','Post Over All'),('jacket_post_report_aeroo','Post')],'Report',default='jacket_report_aeroo')

	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.armourer.visit',
			'form' : data
		}
		report_name =  data['report_name']
		
		if report_name == 'jacket_report_aeroo':
			rep = 'sos_uniform.report_jacket_main'
		
		if report_name == 'jacket_center_all_aeroo':
			rep = 'sos_uniform.report_jacket_center_all'
			
		if report_name == 'jacket_center_specific_aeroo':
			rep = 'sos_uniform.report_jacket_center_specific'
			
		if report_name == 'jacket_project_all_aeroo':
			rep = 'sos_uniform.report_jacket_project_all'
			
		if report_name == 'jacket_project_specific_aeroo':
			rep = 'sos_uniform.report_jacket_project_specific'	
			
		if report_name == 'jacket_post_all_aeroo':
			rep = 'sos_uniform.report_jacket_post_all'
			
		if report_name == 'jacket_post_report_aeroo':
			rep = 'sos_uniform.report_jacket_post_specific'

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas)
