import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class SOSCenterPostWiseGuards(models.TransientModel):
	_name = "sos.center.postwise.guards.wizard"
	_description = "Center PostWise Guards Wizard"
	
	center_ids = fields.Many2many('sos.center', string='Projects')

	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.center',
			'form' : data
		}
		return self.env.ref('sos.report_center_postwise_guard_details').with_context(landscape=True).report_action(self, data=datas)
