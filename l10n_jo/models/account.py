# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    @api.model
    def _prepare_liquidity_account(self, name, company, currency_id, type):
        res = super(AccountJournal, self)._prepare_liquidity_account(name, company, currency_id, type)
        group_record = self.env.ref('l10n_jo.account_group_5')
        if group_record:
            res['group_id'] = group_record.id
        return res