import time
import pdb
from odoo import api, fields, models

class SOSGuardsShortFallWizard(models.TransientModel):
	_name = "guards.shortfall.wizard"
	_description = "Guards ShortFall Report"
	
	date_from = fields.Date("Date From",default=lambda *a: time.strftime('%Y-%m-%d'))
	group_by = fields.Selection([('center','By Center'),('project','By Project'), ('post','By Post')],'Group By',default='center')
	
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")                           		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          
		
	
	@api.multi
	def print_report(self):
				
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.shortfall.wizard',
			'form' : data
		}
		
		report_name =  data['group_by']
		
		if report_name == 'center':
			rep = 'sos_payroll.report_shortfall_center'
		
		if report_name == 'project':
			rep = 'sos_payroll.report_shortfall_project'
			
		if report_name == 'post':
			rep = 'sos_payroll.report_shortfall_post'

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas)
			
