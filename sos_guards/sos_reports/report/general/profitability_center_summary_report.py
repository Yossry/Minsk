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


class ReportProfitabilityCenterSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_profitabilitysummarycenter'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def get_admin_exp_account(self,center):
		account_id = False
		if center.name:
			if center.id == 23:
				account_id = 109 #41031 Bahawalpur Office Administration Exp
			if center.id == 30:
				account_id = 270 #41078 D.G Khan Office Administration Exp
			if center.id == 26:
				account_id = 268 #41076 Faisalabad Office Administration Exp
			if  center.id == 34:			
				account_id = 281 #41089 Gilgit Office Administration Exp
			if center.id == 37:
				account_id = 266 #41074 Gujrawala Office Administration Exp
			if center.id == 22:
				account_id = 271 #41079 Hyderabad Office Administration Exp
			if center.id ==	20:
				account_id = 282 #41090 Islamabad Office Administration Exp
			if center.id == 16:
				account_id = 265 #41073 Jehlum Office Administration Exp
			if center.id == 25:
				account_id = 276 #41084 Karachi Office Administration Exp
			if center.id == 27:			
				account_id = 264 #41072 Lahore Office Administration Exp
			if center.id == 33:
				account_id = 277 #41085 Mingora Office Administration Exp
			if center.id == 17:
				account_id = 274 #41082 Mirpur Office Administration Exp
			if center.id == 31:
				account_id = 275 #41083 Muzaffarabad Office Administration Exp
			if center.id == 28:
				account_id = 272 #41080 Peshawar Officce Administration Exp
			if  center.id == 21:
				account_id = 273 #41081 Quetta Office Administration Exp
			if center.id == 59:
				account_id = 280 #41088 Rawalpindi Office Administration Exp
			if center.id == 24:
				account_id = 278 #41086 Sahiwal Office Administration Exp
			if center.id == 29:
				account_id = 269 #41077 Sarghoda Office Administration Exp
			if center.id == 86:
				account_id = 317 #41091 Sialkot Office Administration Exp
			if center.id == 18:
				account_id = 279 #41087 Sukkur Office Administration Exp
			return account_id
							

	@api.multi
	def render_html(self, data=None):
		
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		centers = self.env['sos.center'].search([])
		res = []
		
		invoice_amount = 0
		shortfall_amount = 0
		credit_note_amount = 0
		net_invoice_amount = 0
		salary_amount = 0
		rent_amount = 0
		admin_amount = 0
		ammunition_amount = 0
		fine_penalty_amount = 0
		bank_charges_amount = 0
		gross_amount = 0

		for center in centers:
			self.env.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where center_id = %s and journal_id = %s \
				and date_invoice >= %s and date_invoice <= %s and state in ('open','paid') and inv_type != 'credit'",(center.id,1,date_from,date_to))
			invoiced_data = self.env.cr.dictfetchall()[0]	
			invoiced = int(invoiced_data['amount_untaxed'] or 0)
			
			self.env.cr.execute("select sum(amount_untaxed) as amount_total from account_invoice where center_id = %s and journal_id = %s \
				and date_invoice >= %s and date_invoice <= %s and state in ('open','paid') and inv_type = 'credit'",(center.id,1,date_from,date_to))
			credit_note_data = self.env.cr.dictfetchall()[0]
			credit_note = int(credit_note_data['amount_total'] or 0)
			
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s and aml.journal_id = %s",(date_from,date_to,center.id,29))
			shortfall_data = self.env.cr.dictfetchall()[0]
			shortfall = int(shortfall_data['amount'] or 0)
			
			net_invoiced = invoiced - credit_note - shortfall

			#Salary Expense
			salary = 0
			sql = """select  sum(gpl.total) as salary_expense from guards_payslip gp, guards_payslip_line gpl, sos_center c
					where gpl.slip_id  = gp.id and gpl.code = 'BASIC' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and c.id = gp.center_id and c.id = %s and c.region_id is not null""" % (date_from,date_to,center.id,)	
			self.env.cr.execute(sql)		
			salary = self.env.cr.dictfetchall()[0]['salary_expense'] or 0
			
			#Rent Expense
			rent = 0
			if center.region_id:
				sql = """select c.name, sum(aml.debit) as rent_amt from account_move am,account_move_line aml, sos_region reg,sos_center c 
						where am.id = aml.move_id and aml.account_id = 124 and reg.analytic_region_id = aml.a4_id and c.region_id = reg.id 
						and c.id =%s and am.date >='%s' and am.date <='%s' group by c.name""" %(center.id,date_from,date_to,)
				self.env.cr.execute(sql)
				rent = self.env.cr.dictfetchall()[0]['rent_amt'] or 0
			
			#Admin Expense
			admin = 0
			account_id = self.get_admin_exp_account(center)
			if account_id:
				sql = """select aml.account_id, sum(aml.debit) as admin_amt from account_move am, account_move_line aml 
						where am.id = aml.move_id and am.date >= '%s' and am.date <= '%s' and aml.account_id=%s group by aml.account_id""" %(date_from,date_to,account_id,)
				self.env.cr.execute(sql)
				admin_dt = self.env.cr.dictfetchall()
				if admin_dt:	
					admin =admin_dt[0]['admin_amt'] or 0
				
			#Ammunition Exp 
			ammunition = 0
			if center.region_id:
				sql = """select c.name, sum(aml.debit) as ammunition_amt from account_move am,account_move_line aml, sos_region reg,sos_center c 
						where am.id = aml.move_id and aml.account_id = 140 and reg.analytic_region_id = aml.a4_id and c.region_id = reg.id 
						and c.id =%s and am.date >='%s' and am.date <='%s' group by c.name""" %(center.id,date_from,date_to,)
				self.env.cr.execute(sql)
				ammunition_dt = self.env.cr.dictfetchall()
				if ammunition_dt:
					ammunition = ammunition_dt[0]['ammunition_amt'] or 0
					
			#Fine & Penalty Exp 
			fine_penalty = 0
			if center.region_id:
				sql = """select c.name, sum(aml.debit) as fine_penalty_amt from account_move am,account_move_line aml, sos_region reg,sos_center c 
						where am.id = aml.move_id and aml.account_id = 108 and reg.analytic_region_id = aml.a4_id and c.region_id = reg.id 
						and c.id =%s and am.date >='%s' and am.date <='%s' group by c.name""" %(center.id,date_from,date_to,)
				self.env.cr.execute(sql)
				fine_penalty_dt = self.env.cr.dictfetchall()
				if fine_penalty_dt:
					fine_penalty = fine_penalty_dt[0]['fine_penalty_amt'] or 0
			
			#Bank Charges 
			bank_charges = 0
			if center.region_id:
				sql = """select c.name, sum(aml.debit) as bank_charges_amt from account_move am,account_move_line aml, sos_region reg,sos_center c 
						where am.id = aml.move_id and aml.account_id = 130 and reg.analytic_region_id = aml.a4_id and c.region_id = reg.id 
						and c.id =%s and am.date >='%s' and am.date <='%s' group by c.name""" %(center.id,date_from,date_to,)
				self.env.cr.execute(sql)
				bank_charges_dt = self.env.cr.dictfetchall()
				if bank_charges_dt:
					bank_charges = bank_charges_dt[0]['bank_charges_amt'] or 0						
			
			
			gross = (net_invoiced) - (salary + rent + admin + ammunition + fine_penalty + bank_charges)
			res.append({
				'name': center.name,
				'invoiced': invoiced,
				'shortfall': shortfall or 0,
				'credit_note': credit_note or 0,
				'net_invoiced': net_invoiced or 0,
				'salary': salary or 0,
				'rent': rent or 0,
				'admin': admin or 0,
				'ammunition': ammunition or 0,
				'fine_penalty': fine_penalty or 0,
				'bank_charges': bank_charges or 0,
				'gross': gross or 0,
				})
			
			invoice_amount += invoiced or 0
			shortfall_amount += shortfall or 0
			credit_note_amount += credit_note or 0
			net_invoice_amount += net_invoiced or 0
			salary_amount += salary or 0
			rent_amount += rent or 0
			admin_amount += admin or 0
			ammunition_amount += ammunition or 0
			fine_penalty_amount += fine_penalty or 0
			bank_charges_amount += bank_charges or 0
			gross_amount += gross or 0	
		
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_profitabilitysummarycenter')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"Invoiced" : invoice_amount,
			"ShortFall" : shortfall_amount,
			"Credit_Note" : credit_note_amount,
			"Net" : net_invoice_amount,
			"Salary" : salary_amount,
			"Rent" : rent_amount,
			"Admin" : admin_amount,
			"Ammunition" : ammunition_amount,
			"Fine_Penalty" : fine_penalty_amount,
			"Bank_Charges" : bank_charges_amount,
			"Gross" : gross_amount,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_profitabilitysummarycenter', docargs)
		
