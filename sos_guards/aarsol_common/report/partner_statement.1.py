
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError
from openerp import api, models

import pdb
import time

class PartnerStatementReport(models.AbstractModel):
	_name = 'report.hig_ext.report_partnerstatement'

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
			SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, 
				"account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
			FROM account_move_line
			LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
			LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
			LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
			LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
			WHERE "account_move_line".partner_id = %s
				AND m.state IN %s
				AND "account_move_line".account_id IN %s
				ORDER BY "account_move_line".date"""
	
		self.env.cr.execute(query, tuple(params))
		res = self.env.cr.dictfetchall()
		sum = 0.0
		for r in res:
			r['displayed_name'] = '-'.join(
				r[field_name] for field_name in ('move_name', 'ref', 'name')
				if r[field_name] not in (None, '', '/')
			)
			sum += r['debit'] - r['credit']
			r['progress'] = sum
			full_account.append(r)
		return full_account

	@api.multi
	def render_html(self, data=None):
			
		docargs = {
			'doc_ids': self._ids,
			'doc_model': self.env['res.partner'],
			'docs': self.env['res.partner'].browse(data['form']['partner_id'][0]),
			'lines': self._lines,
		}
	
		return self.env['report'].render('hig_ext.report_partnerstatement', docargs)



		







