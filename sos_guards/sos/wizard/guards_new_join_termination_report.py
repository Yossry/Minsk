
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, fields, models

class sos_guards_new_join_termination_report(models.TransientModel):

	_name = 'sos.guards.new.join.termination.report'
	_description = 'Guard Join and Termination Report'

	center_id = fields.Many2one('sos.center', string='Centers')
	date_from = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])

	@api.multi
	def print_report(self):
		datas = {'ids': self._context.get('active_ids', [])}
		datas.update({'form': self.read([])[0]})
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'guards_new_join_termination_report_aeroo',
			'datas': datas,
		}

	
