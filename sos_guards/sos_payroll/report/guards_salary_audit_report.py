import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter


class ReportAuditGuardsSalary(models.AbstractModel):
	_name = 'report.sos_payroll.report_audit_guardsalary'
	_description = 'Guards Audit Salary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	def _get_posts_guards(self, post_ids, start_date, stop_date):
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and att.name >= %s and att.name <= %s and att.post_id in %s order by to_number(code, '999999')"""
		
		try:
			self.env.cr.execute(sql, (start_date, stop_date, tuple(post_ids),))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise
		return  [x['employee_id'] for x in res] or []
		
		
	def _get_centers_guards(self, center_ids, start_date, stop_date):
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and att.name >= %s and att.name <= %s and att.center_id in %s order by to_number(code, '999999')"""
				
		try:
			self.env.cr.execute(sql, (start_date, stop_date, tuple(center_ids),))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise
		return  [x['employee_id'] for x in res] or []
	
	
	def _get_projects_guards(self, project_ids, start_date, stop_date):
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and att.name >= %s and att.name <= %s and att.project_id in %s order by to_number(code, '999999')"""
						
		try:
			self.env.cr.execute(sql, (start_date, stop_date, tuple(project_ids),))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise
	
		return  [x['employee_id'] for x in res] or []			
	
		
	def get_guards(self,data):
		guard_obj = self.env['hr.employee']
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']			
		
		guard_ids = data['form']['guard_ids']
		
		if not guard_ids:
			post_ids = data['form']['post_ids']				
			if post_ids:
				guard_ids = self._get_posts_guards(post_ids, start_date, stop_date)
		
		if not guard_ids:
			center_ids = data['form']['center_ids']				
			if center_ids:
				guard_ids = self._get_centers_guards(center_ids, start_date, stop_date)
				
		if not guard_ids:
			project_ids = data['form']['project_ids']				
			if project_ids:
				guard_ids = self._get_projects_guards(project_ids, start_date, stop_date)
			
		guards = guard_ids and guard_obj.browse(guard_ids) or []	
		#self.date_start = start_date
		#self.date_stop = stop_date		
		return guards
		
		
	def guard_code_salary(self, guard_id, codes, data):
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']
		sql="""select sum(t.total) amount from guards_payslip_line t 
			left join guards_payslip pl on (t.slip_id = pl.id) 
			where pl.employee_id = %s and pl.date_from >= %s and pl.date_to <= %s and t.code = %s"""
		self.env.cr.execute(sql,(guard_id,start_date,stop_date,codes))		
		amt = self.env.cr.dictfetchone()['amount'] or 0
		return amt
		
	def get_audit_salary_lines(self, emp_id,data):
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']		
		
		sql ="""SELECT emp.id guardid, t.post_id, partner.name postname, pl.number slipnumber, pl.state slipstatus, t.rate guardrate,t.quantity dutydays, t.total salaryamt, gc.name as contract_name, inv.id invoiceid, inv.number invnumber, inv.state invstate
		 	FROM guards_payslip_line t 
		 	LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
		 	LEFT JOIN sos_post post on (t.post_id=post.id)
			LEFT JOIN res_partner partner on (post.partner_id = partner.id)
		 	LEFT JOIN guards_payslip pl on (t.slip_id=pl.id)
		 	LEFT JOIN guards_contract gc on (pl.contract_id=gc.id)
			LEFT JOIN account_invoice inv on (t.post_id = inv.post_id)
		 	WHERE emp.id = %s and pl.date_from >= %s and pl.date_to <= %s and t.code='BASIC' and inv.date_from >= %s and inv.date_to <= %s """		 			
		 	
		try:
			self.env.cr.execute(sql, (emp_id, start_date, stop_date, start_date, stop_date ))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise
		return res or []
		
	
	def get_attendance_days(self, post_id,slip_number):
		sql="""select sum(quantity) days from guards_payslip pl 
			left join guards_payslip_line t on (t.slip_id = pl.id) 
			where pl.post_id = %s and code='BASIC' and pl.number = %s"""
		self.env.cr.execute(sql,(post_id,slip_number))		
		return self.env.cr.dictfetchone()['days'] or 0
	
	
	def get_invoice_days(self, invoice_id):
		days = 0
		if invoice_id:
			sql="""select sum(quantity) days from account_invoice_line where invoice_id = %s"""
			self.env.cr.execute(sql%invoice_id)		
			days = self.env.cr.dictfetchone()['days'] or 0
		return days				
		
	
	
	@api.model
	def _get_report_values(self, docids, data=None):
		line_ids = []
		res = {}
		
		if data['form']['group_by'] == 'sos_report_audit_salary_aeroo':
			guards = self.get_guards(data)
			
			for guard in guards:
				alw_amt = 0
				
				gross_amt = self.guard_code_salary(guard.id,'BASIC',data) or 0
				bonus = self.guard_code_salary(guard.id,'BONUS',data) or 0
				dalw = self.guard_code_salary(guard.id,'DALW',data) or 0
				wp = self.guard_code_salary(guard.id,'WP',data) or 0
				att_alw = self.guard_code_salary(guard.id,'ATTINC',data) or 0
				
				adv_amt = self.guard_code_salary(guard.id,'ADV',data) or 0
				ud_amt =  self.guard_code_salary(guard.id,'UD',data) or 0
				net_amt = self.guard_code_salary(guard.id,'NET',data) or 0
				
				alw_amt = bonus + dalw + wp + att_alw
				
				audit_lines = self.get_audit_salary_lines(guard.id,data)
				for audit_line in audit_lines:
					sal_days = self.get_attendance_days(audit_line['post_id'],audit_line['slipnumber']) or 0
					inv_days = self.get_invoice_days(audit_line['invoiceid']) or 0
					diff_days = (sal_days - inv_days) or 0
					
					audit_line['sal_days'] = sal_days or 0 
					audit_line['inv_days'] = inv_days or 0
					audit_line['diff_days'] = diff_days or 0
				
				line=({
					'name' : guard.name,
					'code' : guard.code,
					'Gross_Amt' : gross_amt,
					'ALW' : alw_amt,
					'ADV' : adv_amt,
					'UD' : ud_amt,
					'NET' : net_amt,
					'Audit_Lines' : audit_lines
					})
					
				line_ids.append(line)
			res = line_ids	
				
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_audit_guardsalary')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"Guards" : res,
			"docs": self,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs