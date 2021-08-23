
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class invoices_verification(models.TransientModel):
	_name = 'invoices.verification'
	_description = 'Invoice Verification Report'
	
	project_id = fields.Many2one('sos.project', string = 'Project')
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'account.invoice',
			'form' : data
			}
		return self.env.ref('sos_reports.report_invoices_verification').with_context(landscape=True).report_action(self, data=datas,config=False)
		
		
