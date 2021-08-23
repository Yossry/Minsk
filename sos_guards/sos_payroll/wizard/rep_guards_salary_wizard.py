import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class GuardsSalaryWizard(models.TransientModel):
	_name = "guards.salary.report"
	_description = "Salary Report"
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	group_by = fields.Selection([
							('sos_report_salary_new_aeroo', 'Guards Salary (New)'),
							('sos_report_audit_salary_aeroo', 'Guards Wise (Audit)'),
							('sos_report_salary_aeroo', 'Posts Wise'),], 'Report',default='sos_report_salary_aeroo')
		
	guard_ids = fields.Many2many('hr.employee', string='Filter on Guards', help="""Only selected Guards will be printed. Leave empty to print all Guards.""")
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                              
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")

	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payslip.line',
			'form' : data
		}
		report_name =  data['group_by']
		
		if report_name == 'sos_report_salary_aeroo':
			rep = 'sos_payroll.report_guards_salary'
			landscape_val = False
		if report_name == 'sos_report_audit_salary_aeroo':
			rep = 'sos_payroll.report_guards_salary_aduit'
			landscape_val = False
		if report_name == 'sos_report_salary_new_aeroo':
			rep = 'sos_payroll.report_guards_salary_new'
			landscape_val = True
				
		return self.env.ref(rep).with_context(landscape=landscape_val).report_action(self, data=datas, config=False)
		
		
		
		
		
		
