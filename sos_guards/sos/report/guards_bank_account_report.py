import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class GuardsBankAccountReport(models.AbstractModel):
	_name = 'report.sos.report_bankaccounts'
	_description = 'SOS Bank Accounts Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		projects = data['form']['project_ids'] and data['form']['project_ids'] or False
		centers = data['form']['center_ids'] and data['form']['center_ids'] or False
		#accowner = ([ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')])
		accowners =['selff','acc','rm','sp','other',False]
		
		line_ids = []
		res = {}
		if centers:
			for center in centers:
				center_lines = []
				for accowner in accowners:
					accown = '-'
					guards = self.env['hr.employee'].search([('current','=',True),('is_guard','=',True),('center_id','=',center),('accowner','=',accowners)])
					
					if accowner == 'selff':
						accown = 'Self'
					elif accowner == 'acc':
						accown ='Accountant'
					elif accowner == 'rm':
						accown ='Regional Manager'
					elif accowner == 'sp':
						accown ='Supervisor'
					elif accowner == 'other':
						accown ='Other'
					else:
						accown ='-'
						 	
					center_line=({
						'accowner' : accown,
						'guards' : guards,
						})
					center_lines.append(center_line)
				
				line=({
					'center' : self.env['sos.center'].search([('id','=',center)]).name or '',
					'center_lines' : center_lines or False,
					})
				line_ids.append(line)
		
		
		if not centers and projects:
			for project in projects:
				center_lines = []
				for accowner in accowners:
					accown = '-'
					guards = self.env['hr.employee'].search([('current','=',True),('is_guard','=',True),('project_id','=',project),('accowner','=',accowner)])
					
					if accowner == 'selff':
						accown = 'Self'
					elif accowner == 'acc':
						accown ='Accountant'
					elif accowner == 'rm':
						accown ='Regional Manager'
					elif accowner == 'sp':
						accown ='Supervisor'
					elif accowner == 'other':
						accown ='Other'
					else:
						accown ='-'			
					
						 	
					center_line=({
						'accowner' : accown,
						'guards' : guards,
						})
					center_lines.append(center_line)
				
				line=({
					'center' : self.env['sos.project'].search([('id','=',project)]).name or '',
					'center_lines' : center_lines or False,
					})
				line_ids.append(line)
							
		res = line_ids
		
		report =  self.env['ir.actions.report']._get_report_from_name('sos.report_bankaccounts')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'BankAccounts' : res,
			'get_date_formate' : self.get_date_formate,
		}