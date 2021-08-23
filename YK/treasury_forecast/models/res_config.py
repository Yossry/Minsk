# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)

    fc_account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Accounts for treasury planning',
        help='The accounts selected here are those on which the treasury '
             'planning will be based',)

    @api.multi
    def fc_accounts(self):
        account_list = self.env['account.account'].search([])
        account_ids = []
        for account in account_list:
            if account in self.fc_account_ids:
                account.treasury_planning = True
                account_ids.append(account.id)
            else:
                account.treasury_planning = False
        return account_ids

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # ICPSudo = self.env['ir.config_parameter'].sudo()
        # css_dict = ICPSudo.get_param('treasury_forecast.fc_css_dict')
        treasury_accounts = self.env['account.account'].search(
            [('treasury_planning', '=', True)])

        res.update(fc_account_ids=treasury_accounts.ids,)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.fc_accounts()
