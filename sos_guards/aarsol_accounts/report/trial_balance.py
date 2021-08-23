import pdb
import time
from itertools import groupby
from operator import itemgetter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from pytz import timezone
from odoo import api, models


class ReportTrialBalance(models.AbstractModel):
	_inherit = 'report.account.report_trialbalance'


	def account_layout_lines(self,account_lines=None):
		flag = True

		while flag:
			flag = False
			grouped_lines = []
			account_lines.sort(key=itemgetter("section"))
	
			for key, valuesiter in groupby(account_lines, lambda item: item["section"]):
				group = {}
				group['section_name'] = key
				group['lines'] = list(v for v in valuesiter)
			
				group['ob'] = sum(line['ob'] for line in group['lines'])
				group['debit'] = sum(line['debit'] for line in group['lines'])
				group['credit'] = sum(line['credit'] for line in group['lines'])
				group['balance'] = sum(line['balance'] for line in group['lines'])

				section_id = group['lines'][0]['section_id']
				section = self.env['account.section'].browse(section_id)
					
				group['section_id'] = section.parent_id and section.parent_id.id or False
				group['section'] = section.parent_id and  (section.parent_id.code+'-'+section.parent_id.name) or ''
				
				grouped_lines.append(group)
				if section.parent_id:
					flag = True
		
			account_lines = grouped_lines
				
		return account_lines

	def _get_accounts(self, accounts, display_account):
		""" compute the balance, debit and credit for the provided accounts
			:Arguments:
				`accounts`: list of accounts record,
				`display_account`: it's used to display either all accounts or those accounts which balance is > 0
			:Returns a list of dictionary of Accounts with following key and value
				`name`: Account name,
				`code`: Account code,
				`credit`: total amount of credit,
				`debit`: total amount of debit,
				`balance`: total amount of balance,
		"""

		account_result = {}
		account_ob_result = {}

		# Prepare sql query base on selected parameters from wizard
		tables, where_clause, where_params = self.env['account.move.line']._query_get()
		tables = tables.replace('"','')
		if not tables:
			tables = 'account_move_line'
		wheres = [""]
		if where_clause.strip():
			wheres.append(where_clause.strip())
		filters = " AND ".join(wheres)
				
		# compute the balance, debit and credit for the provided accounts
		request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
		params = (tuple(accounts.ids),) + tuple(where_params)
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
			account_result[row.pop('id')] = row

		filters = " AND ((account_move_line.date < %s) AND (account_move_line.date < %s))"
	
		request = ("SELECT account_id AS id, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
		#params = (tuple(accounts.ids),) + where_params[0]
		
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
			account_ob_result[row.pop('id')] = row

		account_res = []
		for account in accounts:
			res = dict((fn, 0.0) for fn in ['ob','credit', 'debit', 'balance'])
			currency = account.currency_id and account.currency_id or account.company_id.currency_id
			res['code'] = account.code
			res['name'] = account.name
			res['section_id'] = account.account_section.id
			res['section'] = account.account_section and (account.account_section.code+'-'+account.account_section.name) or ''
			if account.id in account_result.keys() or account.id in account_ob_result.keys():
				res['ob'] = account_ob_result.get(account.id,False) and account_ob_result[account.id].get('balance',0) or 0
				res['debit'] = account_result.get(account.id,False) and account_result[account.id].get('debit',0) or 0
				res['credit'] = account_result.get(account.id,False) and account_result[account.id].get('credit',0) or 0
				res['balance'] = (account_ob_result.get(account.id,False) and account_ob_result[account.id].get('balance',0) or 0) + (account_result.get(account.id,False) and account_result[account.id].get('balance',0) or 0)
			if display_account == 'all':
				account_res.append(res)
			if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
				account_res.append(res)
		
		account_res2 = self.account_layout_lines(account_res)		
		return account_res2


	@api.model
	def get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))

		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids'))
		display_account = data['form'].get('display_account')
		accounts = docs if self.model == 'account.account' else self.env['account.account'].search([('company_id','=',self.env.user.company_id.id)])
		account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
		
		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': account_res,
		}
		return docargs
		
		
