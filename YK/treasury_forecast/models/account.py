# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    treasury_planning = fields.Boolean(
        string="Treasury Planning",
        company_dependent=True)


class AccountMove(models.Model):
    """Account move have type depending on their journal for domain purposes"""
    _inherit = "account.move"

    journal_type = fields.Selection(related="journal_id.type")


class AccountMoveLine(models.Model):
    """Move lines are now linked to a treasury forecast depending on the
       treasury date, and thei inherit thei cash flow share 1) from invoice
       or 2) from their account move structure"""
    _inherit = "account.move.line"

    treasury_date = fields.Date(string='Treas. Date')
    forecast_id = fields.Many2one(
        comodel_name='treasury.forecast',
        compute='_compute_treasury_forecast',
        store=True,
        string='Forecast')
    treasury_planning = fields.Boolean(
        compute='_compute_forecast_planning',
        store=True,
        string='FP')
    bank_statement_line_id = fields.Many2one(
        comodel_name='account.bank.statement.line',
        string='Bank statement line',
        store=True)

    @api.depends('account_id.treasury_planning')
    def _compute_forecast_planning(self):
        for account in self:
            account.treasury_planning = account.account_id.treasury_planning

    @api.model
    def create(self, vals):
        """At move line creation the treasury date is equal to the due date"""
        item = super(AccountMoveLine, self).create(vals)
        item.treasury_date = item.date_maturity
        return item

    @api.depends('treasury_date')
    def _compute_treasury_forecast(self):
        """Move line is associated to the treasury forecast
           depending on the treasury date"""
        for item in self:
            if item.treasury_date and item.treasury_planning:
                forecast_obj = self.env['treasury.forecast']
                forecast_id = forecast_obj.search([
                    ('date_start', '<=', item.treasury_date),
                    ('date_end', '>=', item.treasury_date),
                    ('state', '=', 'open')])
                if forecast_id:
                    item.forecast_id = forecast_id[0].id


class AccountJournal(models.Model):
    _inherit = "account.journal"

    treasury_planning = fields.Boolean(string="Treasury Planning")

    @api.model
    def create(self, vals):
        """at creation of a treasury planning journal, the accounts automatically
           created by default are deleted"""
        res = super(AccountJournal, self).create(vals)
        account = res.default_credit_account_id
        if res.treasury_planning:
            account.unlink()
        return res


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date_treasury = fields.Date(string="Treasury Date")

    @api.onchange('date_invoice')
    def onchange_date_invoice(self):
        if self.date_invoice:
            self.date_treasury = self.date_invoice

