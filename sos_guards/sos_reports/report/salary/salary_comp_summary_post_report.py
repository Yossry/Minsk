import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp.tools.translate import _
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class ReportCompSummaryPost(models.AbstractModel):
	_name = 'report.sos_reports.report_compsummarypost'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_period1(self,date_from):
		dt = datetime.strptime(date_from,'%Y-%m-%d')
		dt = str(dt + relativedelta.relativedelta(months=-1))[:10]
		dt = datetime.strptime(dt,'%Y-%m-%d')
		
		period = self.env['sos.period'].search([('date_start','=',dt)])
		return period
	
	def get_period2(self,date_from):
		period = self.env['sos.period'].search([('date_start','=',date_from)])
		return period

			
	@api.multi
	def render_html(self, data=None):
		
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		
		prid1 = self.get_period1(data['form']['date_from']).date_start
		prid2 = self.get_period2(data['form']['date_from']).date_start
		
		center_lines = []
		res = {}
		
		prev_total = 0
		current_total = 0
		diff_total = 0
		
		if center_ids:
			center_ids = self.env['sos.center'].search([('id','in',center_ids)])
			
			for center_id in center_ids:
				project_lines = []
				project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
				
				if project_ids:
					project_ids = self.env['sos.project'].search([('id','in',project_ids)])
					
					for project_id in project_ids:
						p_prev_total = 0
						p_current_total = 0
						p_diff_total = 0
						
						posts = self.env['sos.post'].search([('center_id','=',center_id.id),('project_id','=',project_id.id)])
						
						line_ids = []
						for post in posts:
							self.env.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.date_from = %s and gp.post_id = %s and code = %s and state in ('done')",(prid1,post.id,'BASIC'))
							salary_data = self.env.cr.dictfetchall()[0]
							prev_salary = int(0 if salary_data['amount'] is None else salary_data['amount'])

							self.env.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.date_from = %s and gp.post_id = %s and code = %s and state in ('done')",(prid2,post.id,'BASIC'))
							salary_data = self.env.cr.dictfetchall()[0]
							salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
							
							diff = (salary-prev_salary)
							line = ({
								'post_name': post.name,
								'amount': salary or 0,
								'amount_prev': prev_salary or 0,
								'diff': diff or 0,
							})
							
							line_ids.append(line)
							
							##Project Total
							p_prev_total += prev_salary
							p_current_total += salary
							p_diff_total += diff
						
						##OverAll Total
						prev_total += p_prev_total
						current_total += p_current_total
						diff_total += p_diff_total
						
						
						project_line = ({
							"project_name" : project_id.name,
							"posts" : line_ids,
							"P_Prev_Total" : p_prev_total or 0,
							"P_Current_Total" : p_current_total or 0,
							"P_Diff_Total" : p_diff_total or 0,
							})
						project_lines.append(project_line)		
				
				
				center_line = ({
					"center_name" : center_id.name,
					"projects" : project_lines,
					})
				center_lines.append(center_line)
			res = center_lines
		
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_compsummarypost')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Period1" : self.get_period1,
			"Period2" : self.get_period2,
			"Records" : res or False,
			"Prev_Total" : prev_total or 0,
			"Current_Total" : current_total or 0,
			"Diff_Total" : diff_total or 0,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_compsummarypost', docargs)
		
