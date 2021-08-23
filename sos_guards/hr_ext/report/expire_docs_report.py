import pdb
import time
from datetime import datetime, timedelta
from openerp import api, models

class ReportExpireDocs(models.AbstractModel):
	_name = 'report.hr_ext.report_expiredocs'
	_description = 'Employee Expire Docs Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def get_report_values(self, docsid, data=None):	
		status = data['form']['status']
		if status == 'expired':
			doc_ids = self.env['hr.documents.expire'].search([('days_left','<=',0)])
		if status == 'near_to_expired':
			doc_ids = self.env['hr.documents.expire'].search([('expiring','=',True)])
		if status == 'all':
			doc_ids = self.env['hr.documents.expire'].search([])
			
		report = self.env['ir.actions.report']._get_report_from_name('hr_ext.report_expiredocs')
		
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Docs' : doc_ids or False,
			'get_date_formate' : self.get_date_formate,
		}
		return docargs

