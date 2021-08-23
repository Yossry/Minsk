
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, fields, models

class GuardsSalaryExpenseWizard(models.TransientModel):
	_name = "guards.salary.expense.wizard"
	_description = "Salary Expense Report"
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	group_by = fields.Selection([('region_wise_salary_expense', 'Region Wise Report'),	('project_wise_salary_expense', 'Project Wise Report'),], 'Report',default='region_wise_salary_expense')
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                              
	region_ids = fields.Many2many('sos.region', string='Filter on Region', help="""Only selected Region will be printed. Leave empty to print all Region.""")
	
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['group_by'] = data['form']['group_by'] or False
		
		result['project_ids'] = data['form']['project_ids'] or False
		result['region_ids'] = data['form']['region_ids'] or False
			
		return result
	
	
	
	@api.multi
	def print_report(self):		
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		report_name =  data['form']['group_by']
		
		if report_name == 'region_wise_salary_expense':
			rep = 'sos_reports.report_guards_salary_regionwise'
		if report_name == 'project_wise_salary_expense':
			rep = 'sos_reports.report_guards_salary_projectwise'	

		return self.env['report'].with_context(landscape=False).get_action(self, rep, data=data)
		
