import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportGSTPostSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_gst_summarypost'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		
		withheld_amount = 0
		received_amount = 0
		pending_amount = 0
		
		center_lines = []
		res = {}
		tax_amount = 0
		
		if center_ids:
			centers = self.env['sos.center'].search([('id','in', center_ids)])
			for center in centers:
				project_lines = []
				project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
				
				if project_ids:
					projects = self.env['sos.project'].search([('id','in',project_ids)])
					
					for project in projects:
						posts = self.env['sos.post'].search([('center_id','=',center.id),('project_id','=',project.id),('active','=', True)])
						line_ids = []
			
						for post in posts:
							self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 147 \
								and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
							taxed_data = self.env.cr.dictfetchall()[0]
							taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])

							self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 147 \
								and aml.journal_id = 32 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
								
							withheld_data = self.env.cr.dictfetchall()[0]
							withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])

							self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 147 \
								and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
							received_data = self.env.cr.dictfetchall()[0]
							
							received = 0
							if received_data['amount'] and received_data['amount'] > 0:
								received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld

							self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 147 \
								and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
							pending_data = self.env.cr.dictfetchall()[0]
							pending = int(0 if pending_data['amount'] is None else pending_data['amount']) 

							line = ({
								'post_name': post.name,
								'taxed': taxed or 0,
								'withheld': withheld or 0,
								'pending': pending or 0,
								'received': received or 0,				
							})
							line_ids.append(line)
	
							tax_amount += taxed
							withheld_amount += withheld
							received_amount += received
							pending_amount += pending
			
						project_line = ({
								"project_name" : project.name,
								"posts" : line_ids,
								})
						project_lines.append(project_line)
		
				center_line = ({
						"center_name" : center.name,
						"projects" : project_lines,
						})
				center_lines.append(center_line)
			res = center_lines or False

		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_gst_summarypost')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"Taxed" : tax_amount or 0,
			"Withheld" : withheld_amount or 0,
			"Pending" : pending_amount or 0,
			"Received" : received_amount or 0,
			"get_date_formate" : self.get_date_formate,
		}
		return docargs