import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
from openerp import api, models
import pytz, datetime
from dateutil import tz
from openerp import tools
from operator import itemgetter


class ReportPostPendingRecovery(models.AbstractModel):
	_name = 'report.sos_reports.post_report_pendingrecovery'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')		
			
	@api.multi
	def render_html(self, data=None):
	
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
			
		project_ids = data['form']['project_ids'] or False
		center_ids = data['form']['center_ids'] or False
		
		res = []
		total_residual = 0
		posts = False
		
		if project_ids:
			posts = self.env['sos.post'].search([('project_id','in',project_ids)])
		
		if center_ids:
			posts = self.env['sos.post'].search([('center_id','in',center_ids)]) 	
		
		if posts:
			for post in posts:
				residual_amt = 0
				self.env.cr.execute("select sum(residual) as amount from \
					account_invoice where date_invoice >= %s and date_invoice <= %s and post_id = %s and journal_id = 1 and inv_type !='credit'",(date_from,date_to,post.id))
				residual = self.env.cr.dictfetchall()[0]
				residual_amt = int(residual['amount'] or 0)
			
				if residual_amt > 0:
					res.append({
						'name': post.name,
						'residual': int(residual['amount'] or 0) or '0',
						})
				
					total_residual += int(residual['amount'] or 0)	
		
		
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.post_report_pendingrecovery')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts" : res or False,
			"Total_Residual" : total_residual,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.post_report_pendingrecovery', docargs)
		
