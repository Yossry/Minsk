# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import models, fields, api, _


class AccountBankStatement(models.Model):
    """Adding initial and final date to bank statements,
       adding boolean to identify treasury planning statements."""
    _inherit = 'account.bank.statement'
    _description = 'Adding fields for treasury management.'

    treasury_planning = fields.Boolean(
        related='journal_id.treasury_planning',
        store=True, readonly=True)
    initial_date = fields.Date(
        compute='compute_initial_final_date',
        string='Initial Date', store=True)
    final_date = fields.Date(
        compute='compute_initial_final_date',
        string='Final Date', store=True)

    @api.multi
    @api.depends('line_ids')
    def compute_initial_final_date(self):
        """Computing initial and final date of the statement"""
        for statement in self:
            if statement.line_ids:
                line_list = statement.line_ids.sorted(key=lambda r: r.date)
                statement.initial_date = line_list[0].date
                statement.final_date = line_list[-1].date


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    cf_forecast = fields.Boolean(
        string='FC',
        help='This field is flagged if the line is a forecasted transaction')
    statement_fp = fields.Boolean(
        related='statement_id.journal_id.treasury_planning',
        store=True)
    treasury_forecast_id = fields.Many2one(
        comodel_name='treasury.forecast',
        compute='compute_treasury_forecast',
        store=True,
        string='Treasury Forecast')

    amount_main_currency = fields.Monetary(
        string='Amount Main Currency',
        compute='_compute_amount_main_currency',
        store=True,
        help='This field computes the statement line in the Company currency')

    @api.depends('amount', 'journal_id')
    def _compute_amount_main_currency(self):
        for item in self:
            if item.statement_id:
                main_currency = item.company_id.currency_id
                line_currency = item.statement_id.currency_id
                item.amount_main_currency = line_currency.compute(
                    item.amount,
                    main_currency)

    @api.depends('date')
    def compute_treasury_forecast(self):
        """Lines are allocate to treasury forecast based on the date."""
        for item in self:
            # the forecast is the one passed in the context
            force_treasury_id = self._context.get('force_treasury_id', False)
            if force_treasury_id:
                item.treasury_forecast_id = force_treasury_id

            # elsewhere it is computed from the line date
            else:
                forecast_obj = self.env['treasury.forecast']
                forecast_id = forecast_obj.search([
                    ('date_start', '<=', item.date),
                    ('date_end', '>=', item.date),
                    ('state', '=', 'open')])
                if forecast_id:
                    item.treasury_forecast_id = forecast_id[0]

    @api.multi
    def exclude_from_forecast(self):
        for item in self:
            item.cf_forecast = False

    @api.multi
    def include_in_forecast(self):
        for item in self:
            item.cf_forecast = True
