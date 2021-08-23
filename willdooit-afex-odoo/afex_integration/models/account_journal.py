from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    afex_journal = fields.Boolean(
        string='AFEX Journal', default=False, copy=False)
    afex_partner_id = fields.Many2one(
        'res.partner',
        string="AFEX Invoicing Partner",
        copy=False)
    afex_fee_account_id = fields.Many2one(
        'account.account',
        string="AFEX Fees Expense Account",
        domain=[('deprecated', '=', False)],
        copy=False)
    afex_direct_debit_journal_id = fields.Many2one(
        'account.journal', string="Direct Debit Journal", copy=False,
        help=("If this journal settles in AUD, then settlement can be"
              " by direct debit. Choose the Odoo Journal used for direct"
              " debit payments if you wish this to use this option. The"
              " account number for direct debit payments will be picked"
              " up from this journal."))
    afex_direct_debit = fields.Boolean(
        string='Direct Debit by Default', default=False, copy=False,
        help=("Enable this if you want direct debit to be the default"
              " settlement option."))
    afex_scheduled_payment = fields.Boolean(
        string='AFEX Scheduled Payment', default=False, copy=False,
        help=("If journal type is 'Bank', then this can be enabled to create"
              " transactions using pre-purchased funding balances."))

    can_direct_debit = fields.Boolean(
        string='Can direct debit?',
        compute='_compute_can_direct_debit')

    @api.multi
    @api.depends('currency_id')
    def _compute_can_direct_debit(self):
        aud_currency = self.env.ref('base.AUD')
        for journal in self:
            if journal.currency_id == aud_currency:
                journal.can_direct_debit = True
            elif not journal.currency_id and journal.company_id.currency_id == aud_currency:
                journal.can_direct_debit = True
            else:
                journal.can_direct_debit = False

    @api.multi
    @api.constrains('afex_direct_debit_journal_id')
    def _check_direct_debit_journal(self):
        for journal in self:
            if (journal.afex_direct_debit_journal_id
                    and not journal.afex_direct_debit_journal_id.bank_account_id):
                raise UserError(
                    _('Direct Debit Journal has no bank account'))

    @api.model
    def create(self, vals):
        res = super(AccountJournal, self).create(vals)
        res.afex()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountJournal, self).write(vals)
        self.afex()
        return res

    @api.multi
    def afex(self):
        for journal in self.filtered(lambda j: j.afex_journal):
            if journal.type not in ['cash', 'bank']:
                raise UserError(_('AFEX Journals must be of type - Cash/Bank'))
            if journal.inbound_payment_method_ids:
                raise UserError(
                    _('AFEX Journals must not have any associated Inbound'
                      ' Payment Methods (For Incoming Payments)'))
