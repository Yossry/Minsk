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


class ReportProfitabilityProjectCenterSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_profitability_summaryprojectcenter'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.multi
	def render_html(self, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		
		projects = self.env['sos.project'].search([])
		res = []
		
		invoice_amount = 0
		shortfall_amount = 0
		credit_note_amount = 0
		net_invoice_amount = 0
		salary_amount = 0
		gross_amount = 0

		for project in projects:
			self.env.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where project_id = %s and center_id = %s and journal_id = %s \
								and date_invoice >= %s and date_invoice <= %s and state in ('open','paid') and inv_type != 'credit'",(project.id,center_id,1,date_from,date_to))
			invoiced_data = self.env.cr.dictfetchall()[0]	
			invoiced = int(invoiced_data['amount_untaxed'] or 0)

			self.env.cr.execute("select sum(amount_untaxed) as amount_total from account_invoice where project_id = %s and center_id = %s and journal_id = %s \
								and date_invoice >= %s and date_invoice <= %s and state in ('open','paid') and inv_type = 'credit'",(project.id,center_id,1,date_from,date_to))
			credit_note_data = self.env.cr.dictfetchall()[0]
			credit_note = int(credit_note_data['amount_total'] or 0)

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id \
								and aml.date >= %s and aml.date <= %s and ai.project_id = %s and ai.center_id = %s and aml.journal_id = %s",(date_from,date_to,project.id,center_id,29))
			
			shortfall_data = self.env.cr.dictfetchall()[0]
			shortfall = int(shortfall_data['amount'] or 0)
			net_invoiced = invoiced - credit_note - shortfall
			
			salary = 0
			sql = """select  sum(gpl.total) as salary_expense from guards_payslip gp, guards_payslip_line gpl, sos_project p
					where gpl.slip_id  = gp.id and gpl.code = 'BASIC' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and p.id = gp.project_id and p.id = %s and gp.center_id = %s """ % (date_from,date_to,project.id,center_id,)	
			self.env.cr.execute(sql)		
			salary = self.env.cr.dictfetchall()[0]['salary_expense'] or 0
			
			
			
			gross = net_invoiced - salary

			
			res.append({
				'name': project.name,
				'invoiced': invoiced,
				'shortfall': shortfall or 0,
				'credit_note' : credit_note or 0,
				'net_invoiced': net_invoiced or 0,
				'salary': salary or 0,
				'gross': gross or 0,
				})
			
			invoice_amount += invoiced or 0
			shortfall_amount += shortfall or 0
			credit_note_amount += credit_note or 0
			net_invoice_amount += net_invoiced or 0
			salary_amount += salary or 0
			gross_amount += gross or 0	
		
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_profitability_summaryprojectcenter')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Projects" : res or False,
			"Invoiced" : invoice_amount,
			"ShortFall" : shortfall_amount,
			"Credit_Note" : credit_note_amount,
			"Net" : net_invoice_amount,
			"Salary" : salary_amount,
			"Gross" : gross_amount,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_profitability_summaryprojectcenter', docargs)
		
