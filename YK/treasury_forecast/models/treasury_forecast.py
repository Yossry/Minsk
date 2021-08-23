# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from datetime import timedelta
from odoo.exceptions import UserError


class TreasuryForecast(models.Model):
    _name = "treasury.forecast"
    _order = "date_start desc"
    _description = "Treasury Forecast"

    # General data
    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    statement_id = fields.Many2one(string='Statement', comodel_name='account.bank.statement')
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], default='open')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required='True',
                                 default=lambda self: self.env.user.company_id,)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    initial_balance = fields.Float(string='Initial balance', compute='compute_initial_balance',
                                   store=True)
    final_balance = fields.Float(string='Final balance', compute='compute_final_balance',
                                 store=True)
    previous_forecast_id = fields.Many2one(comodel_name='treasury.forecast', string='Previous forecast')
    forecast_template_id = fields.Many2one(comodel_name='treasury.forecast.template', string='Forecast Template')
    periodic_saldo = fields.Float(string='Periodic saldo', compute='_compute_periodic_saldo', store=True)
    hide_analysis = fields.Boolean(string='Hide analysis')
    force_initial_balance = fields.Float(string='Force initial balance')
    set_mass_date = fields.Date(string='Set mass date')

    # detailed analysis fields and text field for reporting table
    payables = fields.Float('Payables', compute='_compute_payables', store=True)
    open_payables = fields.Float('Open payables', compute='_compute_payables', store=True)
    receivables = fields.Float('Receivables', compute='_compute_receivables', store=True)
    open_receivables = fields.Float('Open receivables', compute='_compute_receivables', store=True)
    other_flows = fields.Float('Other flows', compute='_compute_other_flows', store=True)
    open_flows = fields.Float('Open flows', compute='_compute_other_flows', store=True)
    forecast_analysis = fields.Text(string='Treasury Analysis', compute='_compute_periodic_saldo')

    # Payables and receivables
    receivable_ids = fields.One2many(
        comodel_name='account.move.line', inverse_name='forecast_id',
        domain=[('debit', '>', 0), ('journal_id.type', '!=', 'bank')],
        string='Receivables details')
    payable_ids = fields.One2many(
        comodel_name='account.move.line', inverse_name='forecast_id',
        domain=[('credit', '>', 0), ('journal_id.type', '!=', 'bank')],
        string='Payables details')
    recurrent_cost_ids = fields.One2many(
        comodel_name='account.bank.statement.line', inverse_name='treasury_forecast_id',
        string='Cost/revenues', domain=['|', ('statement_fp', '!=', True),
                                        '&', ('statement_fp', '!=', False),
                                        ('cf_forecast', '!=', False)], store=True)

    @api.depends('payable_ids', 'payable_ids.amount_residual')
    def _compute_payables(self):
        for item in self:
            total, due = 0.0, 0.0
            for line in item.payable_ids:
                total += line.balance
                due += line.amount_residual
            item.payables, item.open_payables = total, due

    @api.depends('receivable_ids', 'receivable_ids.amount_residual')
    def _compute_receivables(self):
        for item in self:
            total, due = 0.0, 0.0
            for line in item.receivable_ids:
                total += line.balance
                due += line.amount_residual
            item.receivables, item.open_receivables = total, due

    @api.depends('recurrent_cost_ids', 'recurrent_cost_ids.cf_forecast',
                 'recurrent_cost_ids.amount')
    def _compute_other_flows(self):
        for item in self:
            total, due = 0.0, 0.0
            for line in item.recurrent_cost_ids:
                total += line.amount_main_currency
                fp = line.statement_id.treasury_planning
                due += line.amount_main_currency if fp else 0
            item.other_flows, item.open_flows = total, due

    @api.onchange('previous_forecast_id')
    def _onchange_date_saldo(self):
        for item in self:
            if item.previous_forecast_id:
                date_draft = fields.Date.from_string(
                    item.previous_forecast_id.date_end) + timedelta(days=1)
                item.update({
                    'date_start': fields.Date.to_string(date_draft),
                    'date_end': item.date_start,
                    'initial_balance': item.previous_forecast_id.final_balance
                })

    def _compute_date(self, begin, end, day):
        if day >= 0:
            date_draft = fields.Date.from_string(begin) + timedelta(days=day-1)
        else:
            date_draft = fields.Date.from_string(end) + timedelta(days=day+1)
        date = fields.Date.to_string(date_draft)
        return date

    @api.multi
    def check_constrains(self):
        self.ensure_one()
        # check that there is at least one journal
        if not self.forecast_template_id:
            raise UserError(_("Please select a forecast template."))

    @api.multi
    def compute_forecast_lines(self):
        for item in self:
            self.check_constrains()
            line_ids = []
            for cost in item.forecast_template_id.recurring_line_ids:
                date = self._compute_date(item.date_start, item.date_end, cost.day)
                statement_id = item.forecast_template_id.bank_statement_id.id

                line_ids.append((0, 0, {
                    'name': cost.name,
                    'ref': cost.ref,
                    'partner_id': cost.partner_id.id,
                    'treasury_date': date,
                    'date': date,
                    'amount': cost.amount,
                    'cf_forecast': True,
                    'treasury_forecast_id': item.id,
                    'statement_id': statement_id,
                }))
            item.update({'recurrent_cost_ids': line_ids})
            item.forecast_template_id = ""

    @api.depends('payables', 'open_payables', 'receivables',
                 'open_receivables', 'other_flows', 'open_flows')
    def _compute_periodic_saldo(self):
        for item in self:

            item.periodic_saldo = item.open_receivables + item.open_payables + item.other_flows

            # creating the forecast analysis table
            header = (_(""), _("Receivables"), _("Payables"), _("Other"))
            report_lines = (
                (_("Total"), item.receivables, item.payables, item.other_flows),
                (_("Open"), item.open_receivables, item.open_payables, item.open_flows)
                )

            item.forecast_analysis = self._tuple_to_table(
                'forecast', '', header, None, report_lines)

    def _tuple_to_table(self, kind, css, header, balances, report_lines):
        if kind == 'forecast':
            # creating the table header
            result = "<table class='table' style='{}'> \n<tr>".format(css)
            for head in header:
                result += "<th> {} </th>".format(head)
            result += "\n</tr>\n<tr>"
            if balances:
                for balance in balances:
                    result += "<td> {} </td>".format(formatLang(
                        self.env, balance, 2, monetary=True))
                result += "\n</tr>"

            # creating single lines
            for line in report_lines:
                table_line = "<tr>"
                for value in line:
                    if isinstance(value, str):
                        table_line += "<td> {} </td>".format(value)
                    elif isinstance(value, float):
                        table_line += "<td> {} </td>".format(
                            formatLang(self.env, value, 2, monetary=True))
                table_line += "</tr>"
                result += table_line

            result += "</table>"
        return result

    @api.multi
    def compute_forecast_data(self):
        for item in self:

            # compute treasury date of all account moves
            aml_obj = self.env['account.move.line']
            move_list = aml_obj.search([
                ('treasury_planning', '!=', False),
                ('date_maturity', '>=', item.date_start),
                ('date_maturity', '<=', item.date_end),
                ('forecast_id', '=', False),
            ])
            move_list.update({'forecast_id': item.id})

            bank_line_obj = self.env['account.bank.statement.line']
            bank_line_list = bank_line_obj.search([
                ('date', '>=', item.date_start),
                ('date', '<=', item.date_end),
                ('treasury_forecast_id', '=', False),
                ])
            bank_line_list.update({'treasury_forecast_id': item.id})

    @api.depends('previous_forecast_id.final_balance', 'force_initial_balance')
    def compute_initial_balance(self):
        for item in self:
            if item.previous_forecast_id.final_balance:
                item.initial_balance = item.previous_forecast_id.final_balance

            if item.force_initial_balance != 0.0:
                item.initial_balance = item.force_initial_balance

    @api.depends('initial_balance', 'periodic_saldo')
    def compute_final_balance(self):
        for item in self:
            item.final_balance = item.initial_balance + item.periodic_saldo

    @api.multi
    def refresh_page(self):
        pass

    @api.multi
    def sett_mass_date(self):
        """Once the month is finished we need to move all open items to the next
        forecast. We move all lines with residual different to 0 to the first day."""
        self.ensure_one()
        if not self.set_mass_date:
            raise UserError(_("Please set the date to be set to all open operations."))
        open_moves = self.receivable_ids.filtered(lambda r: r.amount_residual != 0.0)
        open_moves += self.payable_ids.filtered(lambda r: r.amount_residual != 0.0)
        open_moves.update({'treasury_date': self.set_mass_date})
        self.set_mass_date = False
