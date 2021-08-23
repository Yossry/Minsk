import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class GuestHouseWiz(models.TransientModel):
	_name = "guest.house.summary.wiz"
	_description = "Guest House Summary"
		
	check_in = fields.Date('Check In')
	check_out = fields.Date('Check Out')
	need_full_report = fields.Boolean('Need Full Report')
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.guest.house.approval',
			'form' : data
		}
		return self.env.ref('sos_complaint.action_guest_house_summary').with_context(landscape=True).report_action(self, data=datas)
