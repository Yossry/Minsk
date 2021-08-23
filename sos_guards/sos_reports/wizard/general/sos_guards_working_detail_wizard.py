
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import api, fields, models,_
from openerp.exceptions import UserError


class SOSGuardsWorkingDetail(models.TransientModel):
	_name = "sos.guards.working.detail.wizard"
	_description = "Guards Working Detail Wizard"
	
	center_ids = fields.Many2many('sos.center', string='Centers')
	project_ids = fields.Many2many('sos.project', string='Projects')
	post_ids = fields.Many2many('sos.post', string='Posts')
	
	def _build_contexts(self, data):
		result = {}
		result['center_ids'] = data['form']['center_ids'] or False
		result['project_ids'] = data['form']['project_ids'] or False
		result['post_ids'] = data['form']['post_ids'] or False
		return result

	
	@api.multi
	def print_report(self):
				
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})

		return self.env['report'].with_context(landscape=True).get_action(self, 'sos_reports.report_guards_working_detail', data=data)
