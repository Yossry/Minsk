import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from openerp import api, models
import pytz, datetime
from dateutil import tz
from openerp import tools
from operator import itemgetter

class ReportNewGuardsSalary(models.AbstractModel):
	_name = 'report.sos_payroll.report_new_guardsalary'
	_description = 'Guards Salary Report New'
	
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
		
	def	total_salary_days(self, guard_id, data):
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']
		sql="""select sum(w.number_of_days) days from guards_payslip p 
			left join guards_payslip_worked_days w on (w.payslip_id = p.id) 
			where p.employee_id = %s and p.date_from >= %s and p.date_to <= %s"""
		self.env.cr.execute(sql,(guard_id,start_date,stop_date))		
		days = self.env.cr.dictfetchone()['days'] or 0
		return days
		
	def get_audit_salary_lines(self, emp_id,data):
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']		
		
		sql ="""SELECT emp.id guardid, t.post_id, partner.name postname, pl.state slipstatus, t.rate guardrate,t.quantity dutydays, t.total salaryamt, gc.name as contract_name, inv.id invoiceid, inv.number invnumber, inv.state invstate
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
		
	def get_amount_paid_by_advice(self, guard_id, data):
		amt = 0
		slips = self.env['guards.payslip'].search([('employee_id','=',guard_id),('date_from','>=',data['form']['date_from']),('date_to','<=',data['form']['date_to'])])
		if slips:
			for slip in slips:
				if slip.payslip_run_id and slip.advice_id:
					advice_line = self.env['guards.payroll.advice.line'].search([('advice_id','=',slip.advice_id.id),('employee_id','=',guard_id),('slip_id','=',slip.id)])
					amt += advice_line.bysal and advice_line.bysal or 0
		return amt			
		
	@api.model
	def _get_report_values(self, docids, data=None):
		line_ids = []
		res = {}
		
		total_days = 0
		total_paid_by_advice = 0
		total_gross_amt = 0
		total_net_amt = 0
		
		total_security_refund = 0
		total_wp = 0
		total_arrears = 0
		total_bonus = 0
		total_dalw = 0
		total_alw_amt = 0
		
		total_mbl_payroll_amt = 0
		total_adv_amt = 0
		total_security_deposit_amt = 0
		total_fine_amt = 0
		total_ud_amt = 0
		total_debit_balance_amt = 0
		total_excess_salary_amt = 0
		total_provident_fund_amt = 0
		total_deduct_amt = 0
		
		
		if data['form']['group_by'] == 'sos_report_salary_new_aeroo':
			guards = self.get_guards(data)
			for guard in guards:
				audit_line = {}
				alw_amt = 0
				deduct_amt = 0
				
				sal_days = self.total_salary_days(guard.id,data) or 0
				paid_by_advice = self.get_amount_paid_by_advice(guard.id,data) or 0
				gross_amt = self.guard_code_salary(guard.id,'BASIC',data) or 0
				net_amt = self.guard_code_salary(guard.id,'NET',data) or 0	
				
				#Allowance
				bonus = self.guard_code_salary(guard.id,'BONUS',data) or 0			#Bonus Allowance
				dalw = self.guard_code_salary(guard.id,'DALW',data) or 0			#Duty Allowance
				wp = self.guard_code_salary(guard.id,'WP',data) or 0				#Weapon Allowance
				att_alw = self.guard_code_salary(guard.id,'ATTINC',data) or 0 		#Attendance Allowance
				security_refund = self.guard_code_salary(guard.id,'GSDR',data) or 0 #Security Refund
				arrears = self.guard_code_salary(guard.id,'ARRE',data) or 0 		#Arrears
				alw_amt = bonus + dalw + wp + att_alw + security_refund + arrears	# Total Allowance
				
				#Deduction
				adv_amt = self.guard_code_salary(guard.id,'ADV',data) or 0			#Advance Deduction
				ud_amt =  self.guard_code_salary(guard.id,'UD',data) or 0			#Uniform Deduction
				fine_amt = self.guard_code_salary(guard.id,'FINE',data) or 0		#Fine Deduction
				security_deposit_amt = self.guard_code_salary(guard.id,'GSD',data) or 0 #Security Deposit
				
				security_deposit_amt = security_deposit_amt + (self.guard_code_salary(guard.id,'GSD1',data) or 0) #Security Deposit
				
				mbl_payroll_amt = ((self.guard_code_salary(guard.id,'MBLD',data) or 0 ) + (self.guard_code_salary(guard.id,'MBLPC',data) or 0)) #MBL Deduction
				debit_balance_amt = (self.guard_code_salary(guard.id,'434234',data) or 0) #Debit Balance Deduction
				excess_salary_amt = (self.guard_code_salary(guard.id,'EXSP',data) or 0) #Excess Salary Deduction
				provident_fund_amt = (self.guard_code_salary(guard.id,'GPROF',data) or 0) #Provident Fund Deduction
				deduct_amt = adv_amt + ud_amt + fine_amt + security_deposit_amt + mbl_payroll_amt + debit_balance_amt + excess_salary_amt + provident_fund_amt	#Total Deduction
				
				audit_line['sal_days'] = sal_days or 0
				audit_line['paid_by_advice'] = paid_by_advice or 0
				audit_line['net_amt'] = net_amt
				audit_line['gross_amt'] = gross_amt
				audit_line['code'] = guard.code
				audit_line['postname'] = guard.current_post_id.name
				audit_line['name'] = guard.name
				audit_line['center'] = guard.center_id.name
				
				audit_line['bonus'] = bonus
				audit_line['dalw'] = dalw
				audit_line['wp'] = wp
				audit_line['att_alw'] = att_alw
				audit_line['security_refund'] = security_refund
				audit_line['arrears'] = arrears
				audit_line['alw_amt'] = alw_amt
				
				audit_line['adv_amt'] = adv_amt
				audit_line['fine_amt'] = fine_amt
				audit_line['security_deposit_amt'] = security_deposit_amt
				audit_line['ud_amt'] = ud_amt
				audit_line['mbl_payroll_amt'] = mbl_payroll_amt
				audit_line['debit_balance_amt'] = debit_balance_amt
				audit_line['excess_salary_amt'] = excess_salary_amt
				audit_line['provident_fund_amt'] = provident_fund_amt
				audit_line['deduct_amt'] = deduct_amt
			
				line_ids.append(audit_line)
				
				#Totals Calculation
				total_days = total_days + sal_days
				total_paid_by_advice = total_paid_by_advice + paid_by_advice
				total_gross_amt = total_gross_amt + gross_amt
				total_net_amt = total_net_amt + net_amt
				
				total_security_refund = total_security_refund + security_refund
				total_wp = total_wp + wp
				total_arrears = total_arrears + arrears
				total_bonus = total_bonus + bonus
				total_dalw = total_dalw + dalw
				total_alw_amt = total_alw_amt + alw_amt
				
				total_mbl_payroll_amt = total_mbl_payroll_amt + mbl_payroll_amt
				total_adv_amt = total_adv_amt + adv_amt
				total_security_deposit_amt = total_security_deposit_amt + security_deposit_amt
				total_fine_amt = total_fine_amt + fine_amt
				total_ud_amt = total_ud_amt + ud_amt
				total_debit_balance_amt = total_debit_balance_amt + debit_balance_amt
				total_excess_salary_amt = total_excess_salary_amt + excess_salary_amt
				total_provident_fund_amt = total_provident_fund_amt + provident_fund_amt
				total_deduct_amt = total_deduct_amt + deduct_amt
					
			res = line_ids
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_new_guardsalary')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"Guards" : res,
			"Total_Days" : total_days or 0,
			"Total_Paid_By_Advice" : total_paid_by_advice or 0,
			"Total_Gross_Amt" : total_gross_amt or 0, 
			"Total_Net_Amt" : total_net_amt or 0,
			"Total_Security_Refund" : total_security_refund or 0,
			"Total_Wp" : total_wp or 0,
			"Total_Arrears" : total_arrears or 0,
			"Total_Bonus" : total_bonus or 0,
			"Total_Dalw" : total_dalw or 0,
			"Total_Alw_Amt" : total_alw_amt or  0,
			"Total_Mbl_Payroll_Amt" : total_mbl_payroll_amt or  0,
			"Total_Adv_amt" : total_adv_amt or 0,
			"Total_Security_Deposit_Amt" : total_security_deposit_amt or 0,
			"Total_Fine_Amt" : total_fine_amt or 0,
			"Total_Ud_Amt" : total_ud_amt or 0,
			"Total_Debit_Balance_Amt" : total_debit_balance_amt or 0,
			"Total_Excess_Salary_Amt" :  total_excess_salary_amt or  0,
			"Total_Provident_Fund_Amt" :  total_provident_fund_amt or  0,
			"Total_Deduct_Amt" : total_deduct_amt or 0,
			"docs": self,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs
		
