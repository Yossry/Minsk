import time
import pdb
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class AARSOLAccountReportGeneralLedger(models.TransientModel):
	_name = "aarsol.account.report.general.ledger"
	_description = "AARSOL Customized General Ledger Report"

	company_id = fields.Many2one('res.company', string='Company', required=True,default=lambda self: self.env.user.company_id)
	date_from = fields.Date(string='Start Date', required=True)
	date_to = fields.Date(string='End Date', required=True)
	target_move = fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries'), ], string='Target Moves', required=True, default='all')

	display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),('not_zero', 'With balance is not equal to 0'), ],string='Display Accounts', required=True, default='movement')
	initial_balance = fields.Boolean(string='Include Initial Balances',help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
	sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by',required=True, default='sort_date')

	journal_ids = fields.Many2many('account.journal', string='Journals', required=False,default=lambda self: self.env['account.journal'].search([('id', '=', 0)]))
	account_ids = fields.Many2many('account.account', string='Accounts')
	dimension_ids = fields.One2many('ledger.dimension.lines', 'ac_id',string='Dimensions')
	dimension_group = fields.Many2one('analytic.dimension',string="Group by Dimension")

	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['strict_range'] = True if result['date_from'] else False
		result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
		result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
		result['company_id'] = data['form']['company_id'][0] or False
		result['account_ids'] = 'account_ids' in data['form'] and data['form']['account_ids'] or False
		result['display_account'] = data['form']['display_account'] or False
		result['initial_balance'] = data['form']['initial_balance'] or False
		result['sortby'] = data['form']['sortby'] or False
		result['dimension_ids'] = 'dimension_ids' in data['form'] and data['form']['dimension_ids'] or False
		result['dimension_group'] = data['form']['dimension_group'] and data['form']['dimension_group'][0] or False
		return result

	@api.multi
	def check_report(self):
		self.ensure_one()
		data = dict()
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id', 'account_ids','display_account','initial_balance','sortby','dimension_ids','dimension_group'])[0]
		used_context = self._build_contexts(data)
		data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
		#return self.with_context(discard_logo_check=True).pre_print_report(data)
		return self.env.ref('aarsol_accounts.action_aarsol_general_ledger_report').with_context(landscape=True).report_action(self,data=data)


class LedgerDimension(models.TransientModel):
	_name = "ledger.dimension"
	_description = "Ledger Dimensions"
	
	name = fields.Char('Description')	
	ac_lines = fields.One2many('ledger.dimension.lines','ac_id',string="Dimensions")   


class LedgerDimensionLines(models.TransientModel):
	_name = "ledger.dimension.lines"
	_description = "Ledger Dimension Lines"
	
	ac_id = fields.Many2one('aarsol.account.report.general.ledger',string="Ledger Dimension")
	nd_id = fields.Many2one('analytic.dimension',string="Dimension",required=True)
	code_id = fields.Many2one('analytic.code',string="Analytic Value",required=True)
