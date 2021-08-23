import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class SOSProjectGuards(models.TransientModel):
	_name = "sos.project.guards.wizard"
	_description = "Project Guards Wizard"
	
	project_ids = fields.Many2many('sos.project', string='Projects')

	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.project',
			'form' : data
		}
		return self.env.ref('sos.report_project_guard_details').with_context(landscape=True).report_action(self, data=datas)
