
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import api, fields, models

class gst_summary(models.TransientModel):
	_name = "gst.summary"
	_description = 'GST Report'

	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")
	report_name = fields.Selection( [('gst_summary_project_aeroo','Project wise'),('gst_summary_center_aeroo','Center wise'),
									('gst_summary_post_aeroo','Post wise'),('gst_summary_percentage_aeroo','Percentage wise')],'Report',default='gst_summary_project_aeroo')
	percentage = fields.Many2one('account.tax', string = 'GST Percentage')
	
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['report_name'] = data['form']['report_name'] or False
		
		result['project_ids'] = data['form']['project_ids'] or False
		result['center_ids'] = data['form']['center_ids'] or False
		result['percentage'] = data['form']['percentage'] or False
			
		return result
		
	@api.multi
	def print_report(self):		
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		report_name =  data['form']['report_name']
		
		if report_name == 'gst_summary_project_aeroo':
			rep = 'sos_reports.action_report_gst_summaryproject'
		
		if report_name == 'gst_summary_center_aeroo':
			rep = 'sos_reports.action_report_gst_summarycenter'
			
		if report_name == 'gst_summary_post_aeroo':
			rep = 'sos_reports.action_report_gst_summarypost'
			
		if report_name == 'gst_summary_percentage_aeroo':
			rep = 'sos_reports.action_report_gst_summarypercentage'

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=data,config=False)
