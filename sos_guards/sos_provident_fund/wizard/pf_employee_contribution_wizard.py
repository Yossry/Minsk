import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models


class PFEmployeeContributionWizard(models.TransientModel):
	_name = "pf.employee.contribution.wizard"
	_description = "PF Employee Contribution"
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
		
	guard_ids = fields.Many2many('hr.employee', string='Filter on Guards', help="""Only selected Guards will be printed. Leave empty to print all Guards.""")
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                              
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
	
	category = fields.Selection([('Current','Current'),('Inactive','Inactive')], string="Report Catorgy", default='Current')
	from_resign_date = fields.Date('From Resign Date', default=fields.Date.today())
	to_resign_date = fields.Date('To Resign Date', default=fields.Date.today())

	all_projects = fields.Boolean('Include All Projects?')
	all_centers = fields.Boolean('Include All Centers?')

	@api.onchange('all_projects')
	def onchange_all_projects(self):
		if self.all_projects:
			self.all_centers = False

	@api.onchange('all_centers')
	def onchange_all_centers(self):
		if self.all_centers:
			self.all_projects = False

	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_provident_fund.report_pf_employee_contribution').with_context(landscape=True).report_action(self, data=datas)