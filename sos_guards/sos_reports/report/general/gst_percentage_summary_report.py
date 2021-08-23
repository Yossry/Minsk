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


class ReportGSTPercentageSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_gst_summarypercentage'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		percentage = data['form']['percentage'] and data['form']['percentage'][0]
		
		withheld_amount = 0
		received_amount = 0
		pending_amount = 0
		tax_amount = 0
		res = []
		post_ids = []
		
		self.env.cr.execute("select distinct ai.post_id from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = %s and \
		 aml.date >= %s and aml.date <= %s and aml.tax_line_id = %s",(147,date_from,date_to,percentage))
		data_posts = self.env.cr.dictfetchall()
		for post in data_posts:
			post_ids.append(post['post_id'])
			
		posts = self.env['sos.post'].search([('id','in',post_ids)])	
		res = []

		for post in posts:
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 147 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and aml.tax_line_id = %s",(date_from,date_to,post.id,percentage))
			taxed_data = self.env.cr.dictfetchall()[0]
			taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])

			#self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 32 \
			#	and aml.date >= %s and aml.date <= %s and ai.post_id = %s and aml.tax_line_id = %s",(date_from,date_to,post.id,percentage))
			
			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 147 \
				and aml.journal_id = 32 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s and aml.tax_line_id = %s",(date_from,date_to,post.id,percentage))
			withheld_data = self.env.cr.dictfetchall()[0]
			withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 147 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and aml.tax_line_id = %s",(date_from,date_to,post.id,percentage))
			received_data = self.env.cr.dictfetchall()[0]
			received = 0 
			if received_data['amount']  and received_data['amount'] > 0:
				received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 147 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and aml.tax_line_id = %s",(date_from,date_to,post.id,percentage))
			pending_data = self.env.cr.dictfetchall()[0]
			pending = int(0 if pending_data['amount'] is None else pending_data['amount'])  

			res.append({
				'post_name': post.name,
				'taxed': taxed or 0,
				'withheld': withheld or 0,
				'pending': pending or 0,
				'received': received or 0,				
			})
			tax_amount += taxed
			withheld_amount += withheld
			received_amount += received
			pending_amount += pending
			
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_gst_summarypercentage')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts" : res or False,
			"Taxed" : tax_amount or 0,
			"Withheld" : withheld_amount or 0,
			"Pending" : pending_amount or 0,
			"Received" : received_amount or 0,
			"get_date_formate" : self.get_date_formate,
		}
		return docargs