import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportInvoiceCompSummaryProject(models.AbstractModel):
	_name = 'report.sos_reports.report_invoice_compsummaryproject'
	_description = 'Invoice Project Wise Comparsion Summary'	
	
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
			
	@api.model
	def _get_report_values(self, docids, data=None):
		prid1 = self.get_period1(data['form']['date_from']).date_start
		prid2 = self.get_period2(data['form']['date_from']).date_start
		res = []
		prev_total = 0
		current_total = 0
		diff_total = 0
		
		project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
		if project_ids:
			project_ids = self.env['sos.project'].search([('id','in',project_ids)])
		if not project_ids:
			project_ids = self.env['sos.project'].search([])
		
		for project in project_ids:
			
			self.env.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where date_from = %s and project_id = %s and journal_id = %s and state in ('open','paid') and inv_type !='credit'",(prid1,project.id,1))
			dt = self.env.cr.dictfetchall()[0]	

			self.env.cr.execute("select sum(amount_untaxed) as amount_total from account_invoice where date_from = %s and project_id = %s and journal_id = %s and state in ('open','paid') and inv_type ='credit'",(prid1,project.id, 1))
			credit_note = self.env.cr.dictfetchall()[0]
			prev_amount = int(0 if dt['amount_untaxed'] is None else dt['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
	
			self.env.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where date_from = %s and project_id = %s and journal_id = %s and state in ('open','paid') and inv_type !='credit'",(prid2,project.id,1))
			dt = self.env.cr.dictfetchall()[0]	

			self.env.cr.execute("select sum(amount_untaxed) as amount_total from account_invoice where date_from = %s and project_id = %s and journal_id = %s and state in ('open','paid') and inv_type ='credit'",(prid2,project.id,1))
			credit_note = self.env.cr.dictfetchall()[0]
			amount = int(0 if dt['amount_untaxed'] is None else dt['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])

			diff = amount-prev_amount
			res.append({
				'project_name': project.name,
				'amount': amount or 0,
				'amount_prev': prev_amount or 0,
				'diff': diff or 0,
			})

			prev_total += prev_amount
			current_total += amount
			diff_total += diff		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_invoice_compsummaryproject')
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
		
		return docargs