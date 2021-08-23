# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import models, fields, api, _


class TreasuryPlanningTemplate(models.Model):
    """Forecast templates contains recurrent costs to be imported in real
       periodic forecasts"""
    _name = 'treasury.forecast.template'
    _description = 'Treasury Planning Template'

    name = fields.Char(
        string='Template name',
        required=True)
    recurring_line_ids = fields.One2many(
        comodel_name='treasury.forecast.line.template',
        inverse_name='treasury_forecast_template_id',
        string='Recurring Line')
    bank_statement_id = fields.Many2one(
        comodel_name='account.bank.statement',
        string='Bank statement',
        help="Select the virtual bank statement to be used for treasury\
             planning operations",)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required='True',
        default=lambda self: self.env.user.company_id,)


class TreasuryForecastLineTemplate(models.Model):
    _name = 'treasury.forecast.line.template'
    _description = 'Recurring Costs'

    name = fields.Char(string='Label', required=True)
    ref = fields.Char(string='Reference')
    day = fields.Integer(string='Day', required=True, default=0)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')
    amount = fields.Float(string='Amount')
    treasury_forecast_template_id = fields.Many2one(
        'treasury.forecast.template',
        string='Treasury Template')

    @api.constrains('amount')
    def checking_processing_value(self):
        for rec in self:
            if rec.amount == 0:
                raise Warning(_("Each line's amount can not be equal to 0"))
        return True
