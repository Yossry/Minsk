import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class AirTravelSummaryWiz(models.TransientModel):
	_name = "air.travel.summary.wiz"
	_description = "Air Travel Summary"
		
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	need_full_report = fields.Boolean('Need Full Report')

	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.air.reservation',
			'form' : data
		}
		return self.env.ref('sos_complaint.report_airtravel_summary').with_context(landscape=True).report_action(self, data=datas)
