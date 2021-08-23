import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class invoices_comp_summary(models.TransientModel):
	_name = 'invoices.comp.summary'
	_description = 'Invoices Comp Summary Report'
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="Only selected Projects will be printed. Leave empty to print all Projects.")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="Only selected Centers will be printed. Leave empty to print all Centers.")
	report_name = fields.Selection(
				[('invoices_comp_summary_project_aeroo','Project wise Comparison'),
				('invoices_comp_summary_center_aeroo','Center wise Comparison'),
				('invoices_comp_summary_post_aeroo','Post wise Comparison')],
				'Report',default='invoices_comp_summary_project_aeroo')
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'account.invoice',
			'form' : data
			}
		report_name =  datas['form']['report_name']
		
		if report_name == 'invoices_comp_summary_project_aeroo':
			rep = 'sos_reports.report_invoice_comp_summary_project'
		
		if report_name == 'invoices_comp_summary_center_aeroo':
			rep = 'sos_reports.report_invoice_comp_summary_center'
			
		if report_name == 'invoices_comp_summary_post_aeroo':
			rep = 'sos_reports.report_invoice_comp_summary_post'	
			
		return self.env.ref(rep).with_context(landscape=False).report_action(self, data=datas,config=False)
			
		
		
			
