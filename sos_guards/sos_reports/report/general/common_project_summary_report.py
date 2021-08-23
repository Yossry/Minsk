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


class ReportCommonProjectSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_common_summaryproject'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.multi
	def render_html(self, data=None):
		
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		shortfall_amount = 0
		tax_amount = 0
		penalty_amount = 0
		bankcharges_amount = 0
		
		projects = self.env['sos.project'].search([])
		res = []

		for project in projects:
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 29 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			shortfall_data = self.env.cr.dictfetchall()[0]
			shortfall = int(0 if shortfall_data['amount'] is None else shortfall_data['amount'])

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 30 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			tax_data = self.env.cr.dictfetchall()[0]
			tax = int(0 if tax_data['amount'] is None else tax_data['amount'])

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 31 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			penalty_data = self.env.cr.dictfetchall()[0]
			penalty = int(0 if penalty_data['amount'] is None else penalty_data['amount'])

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 35 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			bankcharges_data = self.env.cr.dictfetchall()[0]
			bankcharges = int(0 if bankcharges_data['amount'] is None else bankcharges_data['amount']) 

			res.append({
				'project_name': project.name,
				'shortfall': shortfall or 0,
				'tax': tax or 0,
				'penalty': penalty or 0,
				'bankcharges': bankcharges or 0,				
			})

			shortfall_amount += shortfall or 0
			tax_amount += tax or 0
			penalty_amount += penalty or 0
			bankcharges_amount += bankcharges or 0	
		
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_common_summaryproject')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Projects" : res or False,
			"Shortfall" : shortfall_amount or 0,
			"Tax" : tax_amount or 0,
			"Penalty" : penalty_amount or 0,
			"Bankcharges" : bankcharges_amount or 0,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_common_summaryproject', docargs)
		
