
import time
from datetime import datetime
from dateutil import relativedelta
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
import pdb

class third_party_ledger(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context=None):
		super(third_party_ledger, self).__init__(cr, uid, name, context=context)
		self.init_bal_sum = 0.0
		self.localcontext.update({
			'lines': self.lines,
			'get_partners': self.get_partners,
			'sum_debit_partner': self._sum_debit_partner,
			'sum_credit_partner': self._sum_credit_partner,
			'get_start_date': self._get_start_date,
			'get_end_date': self._get_end_date,
			'get_intial_balance':self._get_intial_balance,				
		})

	def set_context(self, objects, data, ids, report_type=None):
		self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
		self.date_to = data['form'].get('date_to', str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
		self.post_ids = data['form'].get('post_ids')
		self.initial_balance = data['form']['initial_balance']
		return super(third_party_ledger, self).set_context(objects, data, self.post_ids, report_type=report_type)

	def get_partners(self, data):
		post_obj = self.pool.get('sos.post')
		posts = post_obj.browse(self.cr,self.uid,data['form']['post_ids'])		
		return posts

	def _get_start_date(self, data):		
		return self.date_from		

	def _get_end_date(self, data):
		return self.date_to

	def lines(self, partner):
		move_lines = []
		move_obj = self.pool.get('account.move.line')
		
		if self.initial_balance:
			sql = ("SELECT '' AS ldate, '' AS lcode, '' AS lref, '' as mname,'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, \
				COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance FROM account_move_line l \
				LEFT JOIN account_move m ON (l.move_id=m.id) \
				WHERE l.partner_id = %s and l.account_id = %s and l.date < %s")
			
			params = (partner.partner_id.id,48,self.date_from) ##13262 debitors
			self.cr.execute(sql, params)
			for row in self.cr.dictfetchall():
				move_lines.append(row)
		
		sql = ("SELECT l.date AS ldate, j.code AS lcode, l.ref AS lref, m.name AS mname,l.name AS lname, COALESCE(l.debit,0) AS debit, \
				COALESCE(l.credit,0) AS credit, 0 AS balance FROM account_move_line l \
				LEFT JOIN account_move m ON (l.move_id=m.id) \
				JOIN account_journal j ON (l.journal_id=j.id) \
				WHERE l.partner_id = %s and l.account_id = %s and l.date between %s and %s ORDER BY l.date")
			
		params = (partner.partner_id.id,48,self.date_from,self.date_to)
		self.cr.execute(sql, params)
		
		balance = 0
		for row in self.cr.dictfetchall():
			balance += (row['debit'] - row['credit'])
			row['balance'] = balance
			move_lines.append(row)

		return move_lines

	def _get_intial_balance(self, partner):
		move_state = ['draft','posted']
		if self.target_move == 'posted':
			move_state = ['posted']
		if self.reconcil:
			RECONCILE_TAG = " "
		else:
			RECONCILE_TAG = "AND l.reconcile_id IS NULL"
		self.cr.execute(
			"SELECT COALESCE(SUM(l.debit),0.0), COALESCE(SUM(l.credit),0.0), COALESCE(sum(debit-credit), 0.0) " \
			"FROM account_move_line AS l,  " \
			"account_move AS m "
			"WHERE l.partner_id = %s " \
			"AND m.id = l.move_id " \
			"AND m.state IN %s "
			"AND account_id IN %s" \
			" " + RECONCILE_TAG + " "\
			"AND " + self.init_query + "  ",
			(partner.id, tuple(move_state), tuple(self.account_ids)))
		res = self.cr.fetchall()
		self.init_bal_sum = res[0][2]
		return res

	def _sum_debit_partner(self, partner):
		move_state = ['draft','posted']
		if self.target_move == 'posted':
			move_state = ['posted']

		result_tmp = 0.0
		result_init = 0.0
		if self.reconcil:
			RECONCILE_TAG = " "
		else:
			RECONCILE_TAG = "AND reconcile_id IS NULL"
		if self.initial_balance:
			self.cr.execute(
				    "SELECT sum(debit) " \
				    "FROM account_move_line AS l, " \
				    "account_move AS m "
				    "WHERE l.partner_id = %s" \
				        "AND m.id = l.move_id " \
				        "AND m.state IN %s "
				        "AND account_id IN %s" \
				        " " + RECONCILE_TAG + " " \
				        "AND " + self.init_query + " ",
				    (partner.id, tuple(move_state), tuple(self.account_ids)))
			contemp = self.cr.fetchone()
			if contemp != None:
				result_init = contemp[0] or 0.0
			else:
				result_init = result_tmp + 0.0

		self.cr.execute(
				"SELECT sum(debit) " \
				"FROM account_move_line AS l, " \
				"account_move AS m "
				"WHERE l.partner_id = %s " \
				    "AND m.id = l.move_id " \
				    "AND m.state IN %s "
				    "AND account_id IN %s" \
				    " " + RECONCILE_TAG + " " \
				    "AND " + self.query + " ",
				(partner.id, tuple(move_state), tuple(self.account_ids),))

		contemp = self.cr.fetchone()
		if contemp != None:
			result_tmp = contemp[0] or 0.0
		else:
			result_tmp = result_tmp + 0.0

		return result_tmp  + result_init

	def _sum_credit_partner(self, partner):
		move_state = ['draft','posted']
		if self.target_move == 'posted':
			move_state = ['posted']

		result_tmp = 0.0
		result_init = 0.0
		if self.reconcil:
			RECONCILE_TAG = " "
		else:
			RECONCILE_TAG = "AND reconcile_id IS NULL"
		if self.initial_balance:
			self.cr.execute(
				    "SELECT sum(credit) " \
				    "FROM account_move_line AS l, " \
				    "account_move AS m  "
				    "WHERE l.partner_id = %s" \
				        "AND m.id = l.move_id " \
				        "AND m.state IN %s "
				        "AND account_id IN %s" \
				        " " + RECONCILE_TAG + " " \
				        "AND " + self.init_query + " ",
				    (partner.id, tuple(move_state), tuple(self.account_ids)))
			contemp = self.cr.fetchone()
			if contemp != None:
				result_init = contemp[0] or 0.0
			else:
				result_init = result_tmp + 0.0

		self.cr.execute(
				"SELECT sum(credit) " \
				"FROM account_move_line AS l, " \
				"account_move AS m "
				"WHERE l.partner_id=%s " \
				    "AND m.id = l.move_id " \
				    "AND m.state IN %s "
				    "AND account_id IN %s" \
				    " " + RECONCILE_TAG + " " \
				    "AND " + self.query + " ",
				(partner.id, tuple(move_state), tuple(self.account_ids),))

		contemp = self.cr.fetchone()
		if contemp != None:
			result_tmp = contemp[0] or 0.0
		else:
			result_tmp = result_tmp + 0.0
		return result_tmp  + result_init
	

	def _display_initial_balance(self, data):
		if self.initial_balance:
			return True
		return False



class report_postledger(osv.AbstractModel):
	_name = 'report.sos_reports.report_postledger'
	_inherit = 'report.abstract_report'
	_template = 'sos_reports.report_postledger'
	_wrapped_report_class = third_party_ledger




