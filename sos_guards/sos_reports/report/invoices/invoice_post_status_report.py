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


class ReportInvoicePostStatus(models.AbstractModel):
	_name = 'report.sos_reports.report_invoice_poststatus'
	_description = 'Invoice Post Status'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']	
		invoice_obj = self.env['account.invoice']
		
		total_taxed = 0
		total_untaxed = 0
		total_insurance = 0 
		total_shortfall = 0
		total_fine = 0 
		total_tax = 0
		total_writeoff = 0
		total_gst = 0
		total_bankcharges = 0
		total_credit = 0
		total_credit_tax = 0
		total_bad_debits =0
		total_paidon = 0
		total_residual = 0
		total_received = 0
		total = 0
		
		posts = self.env['sos.post'].search([])
		res = []
		
		for post in posts:
			self.env.cr.execute("select sum(debit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 48 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s and ai.inv_type !='credit'",(date_from,date_to,post.id))
			invoiced = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 94 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s and ai.inv_type !='credit'",(date_from,date_to,post.id))
			untaxed = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 146 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			insurance = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 147 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s and ai.inv_type !='credit'",(date_from,date_to,post.id))
			taxed = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(residual) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and post_id = %s and journal_id = 1 and inv_type !='credit'",(date_from,date_to,post.id))
			residual = self.env.cr.dictfetchall()[0]	

			self.env.cr.execute("select sum(amount_untaxed) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and post_id = %s and journal_id = 1 and inv_type ='credit'",(date_from,date_to,post.id))
			credit_note = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(debit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 147 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s and ai.inv_type ='credit'",(date_from,date_to,post.id))
			credit_taxed = self.env.cr.dictfetchall()[0]

			self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.move_id = aml.move_id and aml.account_id = 86 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			paid_on = self.env.cr.dictfetchall()[0]

			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 97 \
				and aml.journal_id =29 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
			shortfall = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 130 \
				and aml.journal_id = 35 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
			bankcharges = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 108 \
				and aml.journal_id = 31 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
			fine = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 147 \
				and aml.journal_id = 32 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
			gst = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select sum(aml.debit) as amount from account_payment ap, account_move_line aml ,account_invoice ai, account_invoice_payment_rel rl where ap.id = aml.payment_id and aml.account_id = 136 \
				and aml.journal_id =37 and aml.date >= %s and aml.date <= %s and ap.id = rl.payment_id and ai.id = rl.invoice_id and ai.post_id = %s",(date_from,date_to,post.id))
			writeoff = self.env.cr.dictfetchall()[0]
						
			received = 0
			tax = 0
			paidon = 0
			
						
			res.append({
				'name': post.name,
				'amount_taxed': int(taxed['amount'] or 0) or '0',
				'amount_untaxed': int(untaxed['amount'] or 0) or '0',
				'amount_total': int(invoiced['amount'] or 0) or '0',
				
				'amount_insurance': int(insurance['amount'] or 0) or '0',
				'amount_credit': int(credit_note['amount'] or 0) or '0',
				'amount_credit_tax': int(credit_taxed['amount'] or 0) or '0',
				'residual': int(residual['amount'] or 0) or '0',
				'received': received,
				
				'amount_shortfall': int(shortfall['amount'] or 0) or '0',
				'amount_fine': int(fine['amount'] or 0) or '0',
				'amount_gst': int(gst['amount'] or 0) or '0',
				'amount_tax': tax,
				
				'amount_writeoff': int(writeoff['amount'] or 0) or '0',
				'bankcharges': int(bankcharges['amount'] or 0) or '0',
				'paidon': paidon,
				
			})
			
			total_taxed += int(taxed['amount'] or 0)
			total_untaxed += int(untaxed['amount'] or 0)
			total_insurance += int(insurance['amount'] or 0)
			total += int(invoiced['amount'] or 0)
			total_residual += int(residual['amount'] or 0)
			
			total_shortfall += int(shortfall['amount'] or 0)
			total_fine += int(fine['amount'] or 0)
			total_gst += int(gst['amount'] or 0)
			total_tax += tax
			
			total_bankcharges += int(bankcharges['amount'] or 0)
			total_writeoff += int(writeoff['amount'] or 0)
			total_credit += int(credit_note['amount'] or 0)
			total_credit_tax += int(credit_taxed['amount'] or 0)
			total_paidon += paidon
			total_received += received	
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_invoice_poststatus')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts" : res or False,
			"Total_Taxed" : total_taxed,
			"Total_Untaxed" : total_untaxed,
			"Total_Insurance" : total_insurance, 
			"Total_Shortfall" : total_shortfall,
			"Total_Fine" : total_fine,
			"Total_Tax" : total_tax,
			"Total_Writeoff" : total_writeoff,
			"Total_Gst" : total_gst,
			"Total_Bankcharges" : total_bankcharges,
			"Total_Credit" : total_credit,
			"Total_Credit_Tax" : total_credit_tax,
			"Total_Bad_debits" : total_bad_debits,
			"Total_Paidon" : total_paidon,
			"Total_Residual" : total_residual,
			"Total_Received" : total_received,
			"Total" : total,
			"get_date_formate" : self.get_date_formate,
		}
		return docargs