import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _

class GuardsDocsComplaiontWizard(models.TransientModel):
	_name = "guards.docs.complaint.wizard"
	_description = "Guards Docs Complaint Wizard"
	
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                              
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos.report_guards_docs_complaint').with_context(landscape=True).report_action(self, data=datas)

