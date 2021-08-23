import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class SOSGuardsDataReport(models.AbstractModel):
	_name = 'report.sos.report_guardsdata'
	_description = 'Guards Data Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		project_id = data['form']['project_id'] and data['form']['project_id'][0] or False
		center_id = data['form']['center_id'] and data['form']['center_id'][0]  or False
		guards_ids = False
		
		if project_id and center_id == False:
			guards_ids = self.env['hr.employee'].search([('project_id', '=', project_id),('current','=',True)],order='current_post_id')
			
		if center_id and project_id == False:
			guards_ids = self.env['hr.employee'].search([('center_id', '=', center_id),('current','=',True)],order='current_post_id')
			
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_guardsdata')
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Guards' : guards_ids or False,
			'get_date_formate' : self.get_date_formate,
		}
		
		
