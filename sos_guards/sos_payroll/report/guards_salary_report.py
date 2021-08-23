import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter


class ReportGuardsSalary(models.AbstractModel):
	_name = 'report.sos_payroll.report_guardsalary'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	def _get_projects_posts(self, project_ids,data,active=True):
		date_from = data['date_from']
		date_to = data['date_to']		
		posts_obj = self.env['sos.post']

		dom = [('project_id', 'in', project_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
		post_ids = posts_obj.search(dom)
		return post_ids
	
	def get_posts(self,data):
		date_from = data['date_from']
		date_to = data['date_to']
		p_obj = self.env['sos.post']
		
		post_ids  = data['post_ids']
		if post_ids:
			post_ids = p_obj.search([('id','in',post_ids)])
		
		if not post_ids:
			center_ids = data['center_ids'] and data['center_ids']
			if center_ids:
				search_period = [('center_id', 'in', center_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
				post_ids = p_obj.search(search_period)

		if not post_ids:
			project_ids= data['project_ids'] and data['project_ids']
			if project_ids:
				post_ids = self._get_projects_posts(project_ids,data,False)
		return post_ids

	def post_salary_lines(self, post_id, data):
		salary_line_obj = self.env['guards.payslip.line']
		date_start = data['date_from']
		date_stop = data['date_to']
		
		search_period = [('date_from', '>=', date_start),('date_to', '<=', date_stop),('post_id', '=', post_id),('code', '=', 'BASIC')]	
		salary_line_ids = salary_line_obj.search(search_period, order='employee_id')
		if not salary_line_ids:
			return []
		lines = self.get_salary_lines(salary_line_ids.ids, 'post')
		for line in lines:
			if line['paid_leaves_post'] and line['paid_leaves_post'] != post_id:
				line['paid_leaves'] = 0
		return lines

	def get_salary_lines(self, salary_line_ids, ord_by):
		if not salary_line_ids:
			return []
		if not isinstance(salary_line_ids, list):
			salary_line_ids = [salary_line_ids]

		monster ="""SELECT t.employee_id, emp.code, t.post_id, emp.name as emp_name,partner.name, pl.number,t.slip_id, pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,
			t.rate,sum(t.quantity) as quantity, sum(t.total) as total,gc.name as contract_name, b.name as bank_name,pl.abl_incentive_amt as incentive,pl.paid_leaves,paid_leaves_post
			FROM guards_payslip_line t 
			LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
			LEFT JOIN sos_post post on (t.post_id=post.id)
			LEFT JOIN res_partner partner on (post.partner_id = partner.id)
			LEFT JOIN guards_payslip pl on (t.slip_id=pl.id)
			LEFT JOIN guards_contract gc on (pl.contract_id=gc.id)
			LEFT JOIN sos_bank b on (pl.bank=b.id)
			WHERE t.id in %s"""
	
		if ord_by == 'guard':
			monster += """ group by t.employee_id,emp.code,t.post_id,emp.name,partner.name,pl.number,t.slip_id,pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,gc.name,b.name,pl.abl_incentive_amt,pl.paid_leaves,pl.paid_leaves_post  order by emp.name"""
		else:
			monster += """ group by t.post_id,t.employee_id,emp.code,emp.name,partner.name,pl.number,t.slip_id,pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,gc.name,b.name,pl.abl_incentive_amt,pl.paid_leaves,pl.paid_leaves_post order by emp.name"""
				
		try:
			self.env.cr.execute(monster, (tuple(salary_line_ids),))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise
		return res or []

	def get_other_salary_lines(self,slip_id,code=False,post_id=False):
		payslip_line_obj = self.env['guards.payslip.line']
		slip_id = slip_id
		code = code
		total = 0
		
		if slip_id and code =='NET':
			total = 0
			other_line = payslip_line_obj.search([('slip_id', '=', slip_id),('code','=','NET')])
			total = other_line.total or 0
		
		if slip_id and code =='Deduction':
			total = 0
			other_lines= payslip_line_obj.search([('slip_id', '=', slip_id),('post_id','=',post_id),('code','in',['UD','GSD','GLD','ADV','GPROF','MBLD','FINE'])])
			for other_line in other_lines:
				total += abs(other_line.total) or 0
		
		if slip_id and code =='Other':
			total = 0
			other_lines= payslip_line_obj.search([('slip_id', '=', slip_id),('post_id','=',post_id),('code','in',['ARRE','WP','DALW'])])
			for other_line in other_lines:
				total += other_line.total or 0				
		return total				
	
	
	
	@api.model
	def	_get_report_values(self, docids, data=None):
		line_ids = []
		res = {}
		
		net_total = 0
		post_net_total = 0
		net_days = 0
		total_present_days = 0
		paid_leaves = 0
		abl_incentive = 0
		total_deductions = 0 
		
		if data['form']['group_by'] == 'sos_report_salary_aeroo':
			posts = self.get_posts(data['form'])
			
			for post in posts:
				post_paid_leaves =0
				post_present_days = 0
				post_days = 0
				post_total = 0
				post_abl_incentive = 0
				post_deductions = 0
				post_net = 0
			
				salary_lines = self.post_salary_lines(post.id,data['form'])
				if salary_lines:
					for salary_line in salary_lines:
					
						slip_net = self.get_other_salary_lines(salary_line['slip_id'],'NET')
						deduction = self.get_other_salary_lines(salary_line['slip_id'],'Deduction',post.id)
						other = self.get_other_salary_lines(salary_line['slip_id'],'Other',post.id)
					
						salary_line['slip_net'] = slip_net or 0
						salary_line['deduction'] = deduction or 0
						salary_line['other'] = other or 0
						salary_line['post_net'] = salary_line['total'] + salary_line['incentive'] + other + - deduction
					
						post_paid_leaves += salary_line['paid_leaves'] or 0
						post_present_days += (salary_line['quantity'] - salary_line['paid_leaves']) or 0
						post_days += salary_line['quantity'] or 0
						post_total += salary_line['total'] or 0
						post_abl_incentive += salary_line['incentive'] or 0
						post_deductions += salary_line['deduction'] or 0
						post_net +=  salary_line['post_net']
				
					net_total += post_total
					post_net_total += post_net
					net_days += post_days
					total_present_days += post_present_days
					paid_leaves += post_paid_leaves
					abl_incentive += post_abl_incentive
					total_deductions += post_deductions 
				
					line=({
						'post_name' : post.name,
						'salary_lines' : salary_lines,
						'post_paid_leaves' : post_paid_leaves,
						'post_present_days' : post_present_days,
						'post_days' : post_days,
						'post_total' : post_total,
						'net_total' : net_total,
						'post_net' : post_net,
						'net_days' : net_days,
						'paid_leaves' : paid_leaves,
						'post_abl_incentive' : post_abl_incentive,
						'post_deductions' : post_deductions,
						})
					
					line_ids.append(line)
				res = line_ids		
						
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_guardsalary')
		docargs =  {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Salary_Recs" : res or False,
			'net_total' : net_total,
			'net_days' : net_days,
			'total_present_days' : total_present_days,
			'paid_leaves' : paid_leaves,
			'abl_incentive' : abl_incentive,
			'total_deductions' : total_deductions,  
			"get_date_formate" : self.get_date_formate,
			'post_net_total' : post_net_total,
		}
		return docargs
		
