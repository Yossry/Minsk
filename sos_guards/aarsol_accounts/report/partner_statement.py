
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo import api, fields, models, _

import pdb
import time

class PartnerStatementReport(models.AbstractModel):
	_name = 'report.aarsol_accounts.partner_statement'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	def _lines(self, partner):
		data = {}
		
		obj_partner = self.env['res.partner']
		data['move_state'] = ['draft', 'posted']
		data['ACCOUNT_TYPE'] = ['payable', 'receivable']

		self.env.cr.execute("""
			SELECT a.id
			FROM account_account a
			WHERE a.internal_type IN %s
			AND NOT a.deprecated""", (tuple(data['ACCOUNT_TYPE']),))
		data['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
		
		full_account = []
		#query_get_data = self.env['account.move.line'].with_context({})._query_get()
		params = [partner.id, tuple(data['move_state']), tuple(data['account_ids'])] 
		query = """
			SELECT aml.id, aml.date, j.code, acc.code as a_code, acc.name as a_name, aml.ref, m.name as move_name, so.name as so_name, so.client_order_ref as client_ref,
				aml.name, aml.debit, aml.credit, aml.amount_currency,aml.currency_id, c.symbol AS currency_code
			FROM account_move_line aml
			LEFT JOIN account_journal j ON (aml.journal_id = j.id)
			LEFT JOIN account_account acc ON (aml.account_id = acc.id)
			LEFT JOIN res_currency c ON (aml.currency_id=c.id)
			LEFT JOIN account_move m ON (m.id=aml.move_id)
			LEFT JOIN account_invoice ai ON (ai.id = aml.invoice_id)
			LEFT JOIN sale_order so ON (so.id = ai.sale_order_id)
			WHERE aml.partner_id = %s
				AND m.state IN %s
				AND aml.account_id IN %s
				ORDER BY aml.date"""
		
		self.env.cr.execute(query, tuple(params))
		res = self.env.cr.dictfetchall()
		sum = 0.0
		for r in res:
			r['displayed_name'] = '-'.join(
				r[field_name] for field_name in ('move_name', 'ref', 'so_name','client_ref')
				if r[field_name] not in (None, '', '/')
			)
			sum += r['debit'] - r['credit']
			r['progress'] = sum
			full_account.append(r)
		return full_account

	@api.model
	def get_report_values(self, docsid, data=None):			
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		report = self.env['ir.actions.report']._get_report_from_name('aarsol_accounts.partner_statement')
		partners = self.env['res.partner'].browse(data['form']['partner_id'][0])
		
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'docs': partners,
			'lines': self._lines,
			'get_date_formate' : self.get_date_formate,
			'data' : data['form'],			
		}					
		return docargs
			
	






