import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import api, fields, models


class PFEmployerContributionWizard(models.TransientModel):
	_name = "pf.employer.contribution.wizard"
	_description = "PF Employee & Employer Contribution"
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
		
	guard_ids = fields.Many2many('hr.employee', string='Filter on Guards', help="""Only selected Guards will be printed. Leave empty to print all Guards.""")
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                              
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")

	category = fields.Selection([('Current', 'Current'), ('Inactive', 'Inactive')], string="Report Catorgy",default='Current')
	from_resign_date = fields.Date('From Resign Date', default=fields.Date.today())
	to_resign_date = fields.Date('To Resign Date', default=fields.Date.today())

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_provident_fund.report_pf_employer_contribution').with_context(landscape=True).report_action(self, data=datas)