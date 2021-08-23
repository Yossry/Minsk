
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, fields, models

class bankcharges_summary(models.TransientModel):

	_name = 'bankcharges.summary'
	_description = 'Bankcharges Report'
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="Only selected Projects will be printed. Leave empty to print all Projects.")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="Only selected Centers will be printed. Leave empty to print all Centers.")
	report_name = fields.Selection( [('common_summary_project_aeroo','Project wise Bank Charges'),('common_summary_center_aeroo','Center wise Bank Charges'),
		('bankcharges_summary_post_aeroo','Post wise Bank Charges')],'Report',default='common_summary_project_aeroo')
		
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['report_name'] = data['form']['report_name'] or False
		
		result['project_ids'] = data['form']['project_ids'] or False
		result['center_ids'] = data['form']['center_ids'] or False
			
		return result
		
		
	@api.multi
	def print_report(self):		
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		report_name =  data['form']['report_name']
		
		if report_name == 'common_summary_project_aeroo':
			rep = 'sos_reports.report_common_summaryproject'
		
		if report_name == 'common_summary_center_aeroo':
			rep = 'sos_reports.report_common_summarycenter'
			
		if report_name == 'bankcharges_summary_post_aeroo':
			rep = 'sos_reports.report_common_summarypost'		

		return self.env['report'].with_context(landscape=False).get_action(self, rep, data=data)
		
		
