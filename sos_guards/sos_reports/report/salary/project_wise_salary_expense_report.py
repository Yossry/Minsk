import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from openerp import api, fields, models, _
from openerp.exceptions import UserError


class ReportProjectWiseSalaryExpense(models.AbstractModel):
	_name = 'report.sos_reports.report_guards_salary_projectwise'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.multi
	def render_html(self, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		project_ids = data['form']['project_ids'] and data['form']['project_ids']
		
		line_ids = []
		res = {}
		
		if project_ids:
			for project_id in project_ids:
				project_rec = self.env['sos.project'].search([('id','=',project_id)])
				
				region_line_ids = []
				post_ids = []
				
				project_salary_expense = 0
				project_uniform_deduction = 0
				project_security_deposit = 0
				project_total = 0
				
				post_ids = project_rec.post_ids
				
				self.env.cr.execute("select distinct region_id as region_id from sos_post where id in %s",(tuple(post_ids.ids),))
				region_ids = self.env.cr.dictfetchall()
				if region_ids:
					for region_id in region_ids:
						salary_expense = 0
						uniform_deduction = 0
						security_deposit = 0
						line_total = 0
					
						region_rec = self.env['sos.region'].search([('id','=',region_id['region_id'])])
						posts = self.env['sos.post'].search([('region_id','=',region_rec.id),('project_id','=',project_rec.id)])
						if posts:
							payslips = self.env['guards.payslip'].search([('post_id','in',posts.ids),('date_from','>=',date_from),('date_to','<=',date_to),('state','=','done')])
							if payslips:
								self.env.cr.execute("select sum(total) as salary_expense from guards_payslip_line where slip_id in %s and post_id in %s and code='BASIC'",(tuple(payslips.ids),tuple(posts.ids),))
								salary_expense = self.env.cr.dictfetchall()[0]['salary_expense'] or 0
								self.env.cr.execute("select sum(total) as uniform_deduction from guards_payslip_line where slip_id in %s and post_id in %s and code='UD'",(tuple(payslips.ids),tuple(posts.ids),))
								uniform_deduction = self.env.cr.dictfetchall()[0]['uniform_deduction'] or 0
								self.env.cr.execute("select sum(total) as security_deposit from guards_payslip_line where slip_id in %s and post_id in %s and code='GSD'",(tuple(payslips.ids),tuple(posts.ids),))
								security_deposit = self.env.cr.dictfetchall()[0]['security_deposit'] or 0
								line_total = salary_expense + uniform_deduction + security_deposit
							
								project_salary_expense += salary_expense
								project_uniform_deduction += uniform_deduction
								project_security_deposit += security_deposit
								project_total += line_total
							
								line=({
									'region_name' : region_rec.name,
									'salary_expense' : salary_expense,
									'uniform_deduction' : uniform_deduction,
									'security_deposit' : security_deposit,
									'line_total' : line_total,
									})
								
								region_line_ids.append(line)
							
				project_line=({
					'project_name' : project_rec.name,
					'region_lines' : region_line_ids,
					'project_salary_expense' : project_salary_expense,
					'project_uniform_deduction' : project_uniform_deduction,
					'project_security_deposit' : project_security_deposit,
					'project_total' : project_total,
					})
				line_ids.append(project_line)
				
		res = line_ids				
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_guards_salary_projectwise')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Projects" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_guards_salary_projectwise', docargs)
		
