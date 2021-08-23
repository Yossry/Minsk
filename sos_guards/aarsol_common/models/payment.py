import time
import pdb
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class account_payment(models.Model):
	_inherit = 'account.payment'

	user_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	payment_type = fields.Selection([('outbound', 'Vendor Payment'), ('inbound', 'Customer Receipt'),('transfer', 'Internal Transfer'),
		('outbound_g', 'General Payment'), ('inbound_g', 'General Receipt')], string='Payment Type', required=True)
	user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
	payment_lines = fields.One2many('account.payment.line', 'payment_id',string='Payment Lines')
	

class account_payment_line(models.Model):
	_name = "account.payment.line"
	_description = "Account Payment Lines"
	
	@api.model
	def _get_currency(self):
		currency = False
		context = self._context or {}
		if context.get('default_journal_id', False):
			currency = self.env['account.journal'].browse(context['default_journal_id']).currency_id
		return currency

	name = fields.Char(required=True, string="Label")
	amount = fields.Monetary(default=0.0, currency_field='company_currency_id')
	amount_currency = fields.Monetary(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,help='Utility field to express amount currency', store=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=_get_currency, help="The optional other currency if it is a multi-currency entry.")
	account_id = fields.Many2one('account.account', string='Account', required=True, index=True, ondelete="cascade", domain=[('deprecated', '=', False)], 
		default=lambda self: self._context.get('account_id', False))
	move_id = fields.Many2one('account.move', string='Journal Entry', ondelete="cascade", help="The move of this entry line.", index=True, required=True, auto_join=True)
	narration = fields.Text(related='move_id.narration', string='Internal Note')
	ref = fields.Char(related='move_id.ref', string='Partner Reference', store=True, copy=False)
	payment_id = fields.Many2one('account.payment', string="Originator Payment", help="Payment that created this entry")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)






