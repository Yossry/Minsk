import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _

class guards_join_termination(models.TransientModel):

	_name = 'guards.join.termination'
	_description = 'Guards Join Termination Report'

	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])     
	order_by = fields.Selection([('post','Post'),('center','Center'),('project','Project'),('appointmentdate','Appointment'),('resigndate','Resign')],'Order By',default='center')
	with_detail = fields.Boolean('Print Detail in Report')

	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.join.termination',
			'form' : data
		}
		return self.env.ref('sos.report_guard_join_termination').with_context(landscape=True).report_action(self, data=datas)
