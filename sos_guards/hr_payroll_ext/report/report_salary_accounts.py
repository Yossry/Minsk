import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
from num2words import num2words

def get_date_formate(sdate):
	ss = datetime.strptime(sdate,'%Y-%m-%d')
	return ss.strftime('%d %b %Y')
		
class ReportSalaryAccounts(models.AbstractModel):
	_name = 'report.hr_payroll_ext.report_salaryaccounts'
	_description = 'HR Accounts Salary Report'

	@api.model
	def get_report_values(self, docsid, data=None):
		date_from = data['date_from']
		date_to = data['date_to']
		company_id = data['company_id']
				
		res = []
		total_credit_amount = 0
		total_debit_amount = 0
		
		self.env.cr.execute("select distinct account_debit as account_id from hr_salary_rule where company_id=%s and active=True and account_debit is not NULL"%(company_id))
		debit_accounts = self.env.cr.dictfetchall()
		
		self.env.cr.execute("select distinct account_credit as account_id from hr_salary_rule where company_id=%s and active=True and account_credit is not NULL"%(company_id))
		credit_accounts = self.env.cr.dictfetchall()
		accounts = debit_accounts + credit_accounts
		
		for acc in accounts:
			acct = self.env['account.account'].search([('id','=',acc['account_id'])])
			
			self.env.cr.execute("select sum(debit) as debit, sum(credit) as credit from account_move_line where company_id=%s and date >=%s and date <=%s and account_id=%s",(company_id,date_from,date_to,acct.id))
			dta = self.env.cr.dictfetchall()[0]
			debit_amount = dta['debit'] or 0
			credit_amount =dta['credit'] or 0
			
			res.append({
				'code' : acct.code or False,
				'account': acct.name,
				'debit_amount': debit_amount,
				'credit_amount': credit_amount,
				})
				
			total_debit_amount += debit_amount or 0
			total_credit_amount += credit_amount or 0 	
			
		report = self.env['ir.actions.report']._get_report_from_name('hr_payroll_ext.report_salaryaccounts')
		slips = self.env['hr.payslip']
		
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'date_from': get_date_formate(date_from),
			'date_to': get_date_formate(date_to),
			'Company': self.env['res.company'].search([('id','=',company_id)]),
			'docs': slips,
			'time': time,
			'Accounts' : res or False,
			'Total_Debit' : total_debit_amount,
			'Total_Credit' : total_credit_amount,			
		}
		return docargs

