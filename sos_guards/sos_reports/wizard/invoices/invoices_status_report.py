import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class invoices_status_report(models.TransientModel):
	_name = 'invoices.status.report'
	_description = 'Invoices Status Report'
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	report_name = fields.Selection(
				[('invoices_status_by_project_aeroo','By Project'),
				('invoices_status_by_center_aeroo','By Center'),
				('invoices_status_by_post_aeroo','By Post')],
				string = 'Report',default='invoices_status_by_project_aeroo')

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
		
		if report_name == 'invoices_status_by_project_aeroo':
			rep = 'sos_reports.report_invoice_project_status'
		
		if report_name == 'invoices_status_by_center_aeroo':
			rep = 'sos_reports.report_invoice_center_status'
			
		if report_name == 'invoices_status_by_post_aeroo':
			rep = 'sos_reports.report_invoice_post_status'
			
		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas,config=False)
		
				
		
		
	


