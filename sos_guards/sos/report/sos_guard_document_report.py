import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _

class SOSGuardDocumentReport(models.AbstractModel):
	_name = 'report.sos.report_guarddocument'
	_description = 'Guard Document Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		rec_obj = self.env['mail.tracking.value']
		
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		date_from = date_from + ' 00:00:01'		
		date_to = date_to + ' 23:59:59'
		
		total = 0
		total_draft = 0
		total_done  = 0
		total_hr = 0
		total_mi = 0
		total_complete =0
		
		 
		self.env.cr.execute ("select u.login as user, \
			sum(case when t.new_value_char='Draft' then 1 end) as draft, \
			sum(case when t.new_value_char='Done' then 1 end) as done, \
			sum(case when t.new_value_char='Hr Review' then 1 end) as hr_review, \
			sum(case when t.new_value_char='MI Review' then 1 end) as mi_review, \
			sum(case when t.new_value_char='Complete' then 1 end) as complete, \
			count(*) as total \
			from mail_tracking_value t,res_users u \
			where t.field = 'profile_status' and t.write_date >= %s and t.write_date <= %s and t.write_uid =u.id \
			group by u.login;", (date_from,date_to));
			
		tt = self.env.cr.dictfetchall()	
		if tt:
			for t in tt:
				total_draft = total_draft + (t['draft'] or 0)
				total_done = total_done + (t['done'] or 0)
				total_hr = total_hr + (t['hr_review'] or 0)
				total_mi = total_mi + (t['mi_review'] or 0)
				total_complete = total_complete + (t['complete'] or 0)
				total = total + (t['total'] or 0)
			
			
		rec_ids = rec_obj.sudo().search([('field','=','profile_status'),('write_date','>=',date_from),('write_date','<=',date_to)],order='write_uid' )	
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_guarddocument')
		
		return {
			'doc_ids': docids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'TT': tt,
			'Total_Draft' : total_draft,
			'Total_Done' : total_done,
			'Total_Hr' : total_hr,
			'Total_Mi' : total_mi,
			'Total_Complete' : total_complete,
			'Total': total,
			'Rec_ids' : rec_ids,
			'get_date_formate' : self.get_date_formate,
		}
		
		
