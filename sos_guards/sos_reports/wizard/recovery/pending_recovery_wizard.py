
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, fields, models

class PendingRecoveryWizard(models.TransientModel):
	_name = "pending.recovery.wizard"
	_description = "Pending Recovery"
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	
	project_ids = fields.Many2many('sos.project', string='Projects')                              
	center_ids = fields.Many2many('sos.center', string='Centers')
	#post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")
	
	group_by = fields.Selection([('sos_project_pending_recovery_report', 'Project Wise Pending Recovery'),
								('sos_center_pending_recovery_report', 'Center Wise Pending Recovery'),	
								('sos_post_pending_recovery_report', 'Post Wise Pending Recovery'),	
								], 'Report',default='sos_project_pending_recovery_report')
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['group_by'] = data['form']['group_by'] or False
		
		#result['post_ids'] = data['form']['post_ids'] or False
		result['project_ids'] = data['form']['project_ids'] or False
		result['center_ids'] = data['form']['center_ids'] or False
			
		return result
		
	@api.onchange('project_ids')
	def onchange_project_ids(self):
		self.center_ids = False
		
	
	@api.onchange('center_ids')
	def onchange_center_ids(self):
		self.project_ids = False
	
	
	
	@api.multi
	def print_report(self):		
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		report_name =  data['form']['group_by']
		
		if report_name == 'sos_project_pending_recovery_report':
			rep = 'sos_reports.project_report_pendingrecovery'
			
		if report_name == 'sos_center_pending_recovery_report':
			rep = 'sos_reports.center_report_pendingrecovery'
			
		if report_name == 'sos_post_pending_recovery_report':
			rep = 'sos_reports.post_report_pendingrecovery'	

		return self.env['report'].with_context(landscape=False).get_action(self, rep, data=data)
		
