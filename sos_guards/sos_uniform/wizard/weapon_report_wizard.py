import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class WeaponReportWizard(models.TransientModel):
	_name = "weapon.report.wizard"
	_description = "Weapon Report Wizard"
	
	date_from = fields.Date("Start Date",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("End Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	center_id = fields.Many2one('sos.center', 'Center')
	project_id = fields.Many2one('sos.project', 'Projects')
	report_name = fields.Selection([('weapon_report_aeroo','Weapon Report'),('weapon_center_all_aeroo','Center Over All'),('weapon_center_specific_aeroo','Specific Center'),('weapon_project_all_aeroo','Project Over All'),('weapon_project_specific_aeroo','Specific Project'),('weapon_post_all_aeroo','Post Over All'),('weapon_post_report_aeroo','Post')],'Report',default='weapon_report_aeroo')

	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'weapon.report.wizard',
			'form' : data
		}
		report_name =  data['form']['report_name']
		
		if report_name == 'weapon_report_aeroo':
			rep = 'sos_uniform.report_weapon_main'
		
		if report_name == 'weapon_center_all_aeroo':
			rep = 'sos_uniform.report_weapon_center_all'
			
		if report_name == 'report_weapon_center_specific':
			rep = 'sos_uniform.report_weaponcenterspecific'
			
		if report_name == 'weapon_project_all_aeroo':
			rep = 'sos_uniform.report_weapon_project_all'
			
		if report_name == 'weapon_project_specific_aeroo':
			rep = 'sos_uniform.report_weapon_project_specific'	
			
		if report_name == 'weapon_post_all_aeroo':
			rep = 'sos_uniform.report_weapon_post_all'
			
		if report_name == 'weapon_post_report_aeroo':
			rep = 'sos_uniform.report_weapon_post_specific'

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas)
				
