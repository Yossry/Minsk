import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _

class daily_clients_visit(models.TransientModel):

	_name = 'daily.clients.visit'
	_description = 'Daily Clients Visit Report'
	
	date_from = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_end = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now())[:10])
	type = fields.Selection([('supervisor','Supervisor'),('am','Am'),('rm','RM'),('all','All')],'Visitor Type',default='supervisor')	
	
	@api.multi
	def print_report(self):
		self.ensure_one()		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.clients.visit',
			'form' : data
		}
		return self.env.ref('sos.report_clients_visit').with_context(landscape=True).report_action(self, data=datas)
