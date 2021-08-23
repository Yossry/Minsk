import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AdditionalGuardReport(models.TransientModel):
	_name = "additional.guard.report"
	_description = "Additional Guard Report Wizard"
		
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now())[:10])

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.additional.guard.proforma',
			'form' : data
		}
		return self.env.ref('sos_complaint.report_additional_guard').with_context(landscape=True).report_action(self, data=datas)
