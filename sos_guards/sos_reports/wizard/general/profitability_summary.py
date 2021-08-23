
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, fields, models

class profitability_summary(models.TransientModel):

	_name = 'profitability.summary'
	_description = 'Profitability Summary Report'
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	center_id = fields.Many2one('sos.center','Center')
	project_id = fields.Many2one('sos.project','Project')
	report_name = fields.Selection( [('profitability_summary_project_aeroo','Project wise Profitability'),
		('profitability_summary_center_aeroo','Center wise Profitability'),
		('profitability_summary_project_center_aeroo','Center Profitability'),
		('profitability_summary_center_project_aeroo','Project Profitability')],'Report',default='profitability_summary_project_aeroo')
	
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['report_name'] = data['form']['report_name'] or False
		
		result['project_id'] = data['form']['project_id'] or False
		result['center_id'] = data['form']['center_id'] or False
			
		return result
		
		
	@api.multi
	def print_report(self):		
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		report_name =  data['form']['report_name']
		
		if report_name == 'profitability_summary_project_aeroo':
			rep = 'sos_reports.report_profitabilitysummaryproject'
		
		if report_name == 'profitability_summary_center_aeroo':
			rep = 'sos_reports.report_profitabilitysummarycenter'
			
		if report_name == 'profitability_summary_project_center_aeroo':
			rep = 'sos_reports.report_profitability_summaryprojectcenter'
			
		if report_name == 'profitability_summary_center_project_aeroo':
			rep = 'sos_reports.report_profitability_summarycenterproject'			

		return self.env['report'].with_context(landscape=True).get_action(self, rep, data=data)
		
