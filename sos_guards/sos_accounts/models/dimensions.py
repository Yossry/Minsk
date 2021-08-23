import pdb
import time
import math
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from odoo import netsvc
from lxml import etree
from odoo.tools import config
from odoo.addons.analytic_structure.MetaAnalytic import MetaAnalytic
from odoo.osv import expression


class SOSProject(models.Model, metaclass = MetaAnalytic):
	_name = 'sos.project'
	_inherit = 'sos.project'
	_bound_dimension_id = False

	_dimension = {
		'name': 'Project',
		'column': 'analytic_project_id',
		'ref_module': 'sos',
		'rel_code' : 'accountno',
		'rel_name' : 'accountno',		
	}


class SOSRegion(models.Model, metaclass = MetaAnalytic):
	_name = 'sos.region'
	_inherit = 'sos.region'

	_dimension = {
		'name': 'Region',
		'column': 'analytic_region_id',
		'ref_module': 'sos',
		'rel_code' : 'code',
		'rel_name' : 'code',		
	}


class AccountAssetDepreciationLine(models.Model):
	_name = 'account.asset.depreciation.line'
	_inherit = 'account.asset.depreciation.line'

	@api.multi
	def create_move(self, post_move=True):
		created_moves = self.env['account.move']
		
		model_rec = self.env['ir.model'].search([('model','=','account.asset.depreciation.line')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')

		for line in self:
			depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
			company_currency = line.asset_id.company_id.currency_id
			current_currency = line.asset_id.currency_id
			amount = current_currency.compute(line.amount, company_currency)
			sign = (line.asset_id.category_id.journal_id.type == 'purchase' or line.asset_id.category_id.journal_id.type == 'sale' and 1) or -1
			asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, line.asset_id.method_number)
			reference = line.asset_id.code
			journal_id = line.asset_id.category_id.journal_id.id
			partner_id = line.asset_id.partner_id.id
			categ_type = line.asset_id.category_id.type
			debit_account = line.asset_id.category_id.account_asset_id.id
			credit_account = line.asset_id.category_id.account_depreciation_id.id
			
			move_line_1 = {
				'name': asset_name,
				'account_id': credit_account,
				'debit': 0.0,
				'credit': amount,
				'journal_id': journal_id,
				'partner_id': partner_id,
				'currency_id': company_currency != current_currency and current_currency.id or False,
				'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
				'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
				'date': depreciation_date,
			}
			number = 0
			for auto_entry in auto_entries:
				move_line_1.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
				ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
				number += math.pow(2,int(ans.ordering)-1)			
			move_line_1.update({'d_bin' : bin(int(number))[2:].zfill(10)})
				
			move_line_2 = {
				'name': asset_name,
				'account_id': debit_account,
				'credit': 0.0,
				'debit': amount,
				'journal_id': journal_id,
				'partner_id': partner_id,
				'currency_id': company_currency != current_currency and current_currency.id or False,
				'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
				'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
				'date': depreciation_date,
			}
			number = 0
			for auto_entry in auto_entries:
				move_line_2.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})				
				ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
				number += math.pow(2,int(ans.ordering)-1)			
			move_line_2.update({'d_bin' : bin(int(number))[2:].zfill(10)})

			move_vals = {
				'ref': reference,
				'date': depreciation_date or False,
				'journal_id': line.asset_id.category_id.journal_id.id,
				'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
				'asset_id': line.asset_id.id,
				}
			move = self.env['account.move'].create(move_vals)
			line.write({'move_id': move.id, 'move_check': True})
			created_moves |= move

		if post_move and created_moves:
			created_moves.post()
		return [x.id for x in created_moves]


class AccountReconciliation(models.AbstractModel):
	_inherit = 'account.reconciliation.widget'

	@api.model
	def _domain_move_lines_for_reconciliation(self, st_line, aml_accounts, partner_id, excluded_ids=None,search_str=False):
		""" Return the domain for account.move.line records which can be used for bank statement reconciliation.

		   :param aml_accounts:  sarfraz
		   :param partner_id:
		   :param excluded_ids:
		   :param search_str:
		"""

		# domain_reconciliation = [
		#  '&', '&',
		#  ('statement_line_id', '=', False),
		#  ('account_id', 'in', aml_accounts),
		#  ('payment_id', '<>', False)
		# ]

		# AARSOL changed the domain
		domain_reconciliation = [
			'&',
			('statement_line_id', '=', False),
			('account_id', 'in', aml_accounts),
		]

		# default domain matching
		domain_matching = expression.AND([
			[('reconciled', '=', False)],
			[('account_id.reconcile', '=', True)]
		])

		domain = expression.OR([domain_reconciliation, domain_matching])
		# AARSOL, Changed the line to if-else
		#if st_line.journal_id.type in ['bank', 'cash']:
		#	domain = domain_reconciliation
		#else:
		#	domain = expression.OR([domain_reconciliation, domain_matching])

		if partner_id:
			domain = expression.AND([domain, [('partner_id', '=', partner_id)]])

		# Domain factorized for all reconciliation use cases
		if search_str:
			str_domain = self._domain_move_lines(search_str=search_str)
			if not partner_id:
				str_domain = expression.OR([
					str_domain,
					[('partner_id.name', 'ilike', search_str)]
				])
			domain = expression.AND([
				domain,
				str_domain
			])

		if excluded_ids:
			domain = expression.AND([
				[('id', 'not in', excluded_ids)],
				domain
			])
		# filter on account.move.line having the same company as the statement line
		domain = expression.AND([domain, [('company_id', '=', st_line.company_id.id)]])

		if st_line.company_id.account_bank_reconciliation_start:
			domain = expression.AND(
				[domain, [('date', '>=', st_line.company_id.account_bank_reconciliation_start)]])
		return domain