# coding: utf-8
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResCompanyCreateWizard(models.TransientModel):
    _inherit = 'res.company.create.wizard'

    # Columns Section
    chart_template_id = fields.Many2one(
        comodel_name='account.chart.template', string='Account Template',
        domain="[('visible', '=', True)]")

    code_digits = fields.Integer(string='# of Digits')

    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Account Currency')

    payable_account_template_id = fields.Many2one(
        comodel_name='account.account.template',
        string='Default Payable Account',
        domain=lambda s: s._get_account_template_domain('payable'))

    receivable_account_template_id = fields.Many2one(
        comodel_name='account.account.template',
        string='Default Receivable Account',
        domain=lambda s: s._get_account_template_domain('receivable'))

    transfer_account_id = fields.Many2one(
        comodel_name='account.account.template', string='Transfer Account',
        domain=lambda s: s._get_account_template_domain('transfer'))

    @api.model
    def _get_account_template_domain(self, type_name):
        domain = []
        if type_name == 'transfer':
            type = self.env.ref('account.data_account_type_current_assets')
            domain += [('reconcile', '=', True)]
        elif type_name == 'receivable':
            type = self.env.ref('account.data_account_type_receivable')
        elif type_name == 'payable':
            type = self.env.ref('account.data_account_type_payable')
        return domain + [('user_type_id', '=', type.id)]

    @api.multi
    def _prepare_chart_wizard(self):
        self.ensure_one()
        return {
            'company_id': self.company_id.id,
            'chart_template_id': self.chart_template_id.id,
            'transfer_account_id': self.transfer_account_id.id,
            'currency_id': self.currency_id.id,
            'code_digits': self.code_digits,
            'sale_tax_id': False,
            'purchase_tax_id': False,
        }

    @api.multi
    def _create_company(self):
        self.ensure_one()
        chart_wizard_obj = self.env['wizard.multi.charts.accounts']
        super(ResCompanyCreateWizard, self)._create_company()
        if self.chart_template_id:
            # Install Chart of Accounts
            chart_wizard = chart_wizard_obj.create(
                self._prepare_chart_wizard())
            chart_wizard.execute()

    # View Section
    @api.onchange('chart_template_id')
    def onchange_chart_template_id(self):
        if self.chart_template_id:
            template = self.chart_template_id
            self.code_digits = template.code_digits
            self.currency_id = template.currency_id and\
                template.currency_id.id or\
                self.env.user.company_id.currency_id.id
            self.transfer_account_id = template.transfer_account_id and\
                template.transfer_account_id.id
            self.payable_account_template_id =\
                template.property_account_payable_id and\
                template.property_account_payable_id.id
            self.receivable_account_template_id =\
                template.property_account_receivable_id and\
                template.property_account_receivable_id.id
