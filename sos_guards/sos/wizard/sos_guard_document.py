import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SOSGuardDocument(models.TransientModel):
	_name = "sos.guard.document"
	_description = "Guard Document Wizard"
		
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now())[:10])
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guard.documents',
			'form' : data
		}
		return self.env.ref('sos.report_sos_guarddocument').with_context(landscape=True).report_action(self, data=datas)
