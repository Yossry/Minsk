# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

import ast
import datetime
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError


class BankBalanceComputation(models.TransientModel):
    """Transient model that, provided given params, return a table with
    bank transactions and a chart table of them."""
    _name = "bank.balance.computation"
    _description = 'Transient model for computing future bank balance'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    default_id = fields.Many2one(
        'bank.balance.configuration', string='Default')
    date_start = fields.Date(
        string='Start', required=True,
        default=fields.Date.today()
        )
    date_end = fields.Date(
        string='End', default=fields.Date.today(),
        required=True)
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Journals',
        domain="[('type', '=', 'bank')]",
        help="""Select all journal about which you want to know the balance.
                By default, all journals will be selected""",
        default=lambda self: self._get_default_journals(),
        )
    bank_balances = fields.Text(string='Bank balances')
    final_query = fields.Text(string='Final Query')

    forecast_options = fields.Boolean(string='CF options')
    detailed_balance = fields.Boolean(string='Detailed balance')
    include_account_moves = fields.Boolean(string='Incl. account moves')

    include_draft_invoices = fields.Boolean(string='Incl. draft invoices')
    include_sale_orders = fields.Boolean(string='Incl. sale orders')
    include_bank_fc_line = fields.Boolean(string='Forec.')

    raw_table = fields.Text('Raw table')
    show_table = fields.Boolean(string='Show table', default=True)
    fc_css_dict = fields.Text(
        string='Dictionary with colours',
        default="""{
            '': '',
            'BNK': '#FFFFFF',
            'FBK': '#D4EFDF',
            'FPL': '#FAFAD2',
            'DFT': '#D7DBDD',
        }""")
    show_chart = fields.Boolean(string='Show chart', default=False)
    bank_balance_chart = fields.Text(string="Bank balance chart")

    # charts configuration parameters
    chart_height = fields.Integer('Chart Height', default=180)
    chart_width = fields.Integer('Chart Width', default=400)

    line_y_bottom = fields.Float('Bottom')
    line_y_top = fields.Float('Top')
    bar_char_height = fields.Float(
        'Height', default=4,
        help="Bar chart height is give by the max amount"
        "volume (in + out) multiplied by this parameter")
    bar_size = fields.Float("Bar size")

    def get_bank_fc_query(self, fc_journal_list, date_start, date_end,
                          company_domain):
        query = """
                UNION

                SELECT CAST('FBK' AS text) AS type, absl.id AS ID, absl.date,
                    absl.name, absl.company_id, absl.amount_main_currency
                    as amount, absl.cf_forecast, journal_id
                FROM account_bank_statement_line absl
                WHERE journal_id IN {}
                    AND date BETWEEN '{}' AND '{}'
                    AND absl.company_id in {}
            """.format(str(fc_journal_list), date_start, date_end,
                       company_domain)
        return query

    def get_acc_move_query(self, date_start, date_end, company_domain):
        query = """
            UNION

            SELECT CAST('FPL' AS text) AS type, aml.id AS ID,
                aml.treasury_date AS date, am.name AS name, aml.company_id,
                aml.amount_residual AS amount, NULL AS cf_forecast,
                NULL AS journal_id
            FROM account_move_line aml
            LEFT JOIN account_move am ON (aml.move_id = am.id)
            WHERE aml.treasury_planning AND aml.amount_residual != 0
                AND aml.treasury_date BETWEEN '{}' AND '{}'
                AND aml.company_id in {}
        """.format(date_start, date_end, company_domain)
        return query

    def get_draft_inv_query(self, date_start, date_end, company_domain):
        query = """
            UNION

            SELECT CAST('DFT' AS text) AS type, ai.id AS ID,
                ai.date_treasury AS date, rp.name AS name, ai.company_id,
                CASE WHEN ai.type = 'out_invoice' THEN
                    ai.amount_total_company_signed ELSE (
                    ai.amount_total_company_signed * -1) END AS amount,
                NULL AS cf_forecast, NULL AS journal_id
            FROM account_invoice ai
            LEFT JOIN res_partner rp ON (ai.partner_id = rp.id)
            WHERE ai.state IN ('draft')
                AND ai.date_treasury BETWEEN '{}' AND '{}'
                AND ai.company_id in {}
        """.format(date_start, date_end, company_domain)
        return query

    def _get_additional_subquery(self, fc_journal_list, date_start, date_end):
        """
        Add here your additional queries inheriting this method and adding
        the query and adding "UNION" at the beginning". See the existing
        additional queries subquery.
        """

        additional_subquery = ""
        company_domain = tuple([self.env.user.company_id.id]*2)

        # adding bank forecasted bank statement lines
        if self.include_bank_fc_line and not fc_journal_list:
            raise UserError(_("Please select at least one "
                              "treasury planning journal."))

        if self.include_bank_fc_line:
            additional_subquery += self.get_bank_fc_query(
                fc_journal_list, date_start, date_end, company_domain)

        # adding account moves, draft invoices.
        # Inherit this method to add new queries
        if self.include_account_moves:
            additional_subquery += self.get_acc_move_query(
                date_start, date_end, company_domain)

        if self.include_draft_invoices:
            additional_subquery += self.get_draft_inv_query(
                date_start, date_end, company_domain)

        return additional_subquery

    @api.multi
    def _get_table_data(self):

        # distinguish between reports with all operation or daily totals
        # 'init_col' indicate the number of columns of the
        # report/table BEFORE journals columns!!
        if not self.detailed_balance:
            journal_header = (_("Date"), _("Cash In"),
                              _("Cash Out"), _("Total"))
            empty_columns = ("", "", "",)
            report_type = "SELECT DISTINCT ON (date) date,"
            css_dict = ""
            init_col = 3
            group_by = ''
        else:
            journal_header = (_("Date"), _("Type"), _("Name"),
                              _("Amount"), _("Total"))
            report_type = "SELECT date, type, name, amount AS amount,"
            empty_columns = ("", "", "", "",)
            css_dict = ast.literal_eval(self.fc_css_dict or {})
            init_col = 4
            group_by = ', id'

        return journal_header, empty_columns, report_type,\
            css_dict, init_col, group_by

    def _get_main_query(self, journal_list, additional_subquery,
                        report_type, total_initial_saldo, journals_balances,
                        daily_volumes, group_by):

        company_domain = tuple([self.env.user.company_id.id] * 2)
        # the main subquery, which always includes ABSL
        main_query = """
            WITH global_forecast AS (
                SELECT CAST('BNK' AS text) AS type, absl.id AS ID, absl.date,
                    absl.name, absl.company_id, absl.amount_main_currency as
                    amount, absl.cf_forecast, journal_id
                FROM account_bank_statement_line absl
                WHERE journal_id IN {_01}
                    AND date BETWEEN '{_02}' AND '{_03}'
                    AND absl.company_id in {_10}
                {_04}
                ORDER BY date, id
            )

            {_05}
            {_08}
            sum(amount) OVER (ORDER BY date {_09}) + {_06},
            {_07} date
            FROM global_forecast
            GROUP BY ID, type, name, date, amount, journal_id
            ORDER BY date, id
        """.format(_01=str(journal_list),  # list of bank journals
                   _02=self.date_start,
                   _03=self.date_end,
                   _04=additional_subquery,  # adding acc. moves, orders, ...
                   _05=report_type,  # all operations or daily totals
                   _06=total_initial_saldo,
                   _07=journals_balances,
                   _08=daily_volumes,
                   _09=group_by,
                   _10=company_domain,
        )

        return main_query

    @api.multi
    def compute_bank_balances(self):
        """Main method to compute bank balance and
        show them in table or graph format """

        self.ensure_one()
        if not self.journal_ids:
            raise UserError(_("Please select at least one bank journal!"))

        currency_id = self.company_id.currency_id
        # col_number is the number of columns in the table,
        # i.e. normal journals (total is excluded)
        col_numb = len(self.journal_ids.filtered(
            lambda j: not j.treasury_planning))

        # get main parameters for the table view
        journal_header, empty_columns, report_type, css_dict, init_col,\
            group_by = self._get_table_data()

        # preparing lists of normal and forecasting
        # list of journal IDs is multiplied by 2 to avoid error on single ID
        journal_list = tuple(
            (k.id for k in self.journal_ids if not k.treasury_planning)) * 2
        fc_journal_list = tuple(
            (k.id for k in self.journal_ids if k.treasury_planning)) * 2

        journals_balances = ""
        balances_list = ()

        total_initial_saldo = 0
        # creating the operation and saldo column for each existing
        # journal which is not for treasury planning
        for journal in self.journal_ids:
            if not journal.treasury_planning:
                initial_balance = self.compute_balance_at_date(
                    journal, self.date_start, currency_id)
                total_initial_saldo += initial_balance
                balances_list += (initial_balance,)
                journals_balances += """
                \nSUM(CASE WHEN journal_id = {} THEN amount ELSE 0 END)
                    OVER (ORDER BY date {}) + {},
                """.format(journal.id, group_by, initial_balance)
                journal_header += (journal.name,)

        all_balances = empty_columns + (total_initial_saldo,) + balances_list
        journal_header += (_("Date"),)

        additional_subquery = self._get_additional_subquery(
            fc_journal_list, self.date_start, self.date_end)

        daily_volumes = ''
        if not self.detailed_balance:
            daily_volumes = """
            sum(CASE WHEN amount > 0 THEN amount ELSE 0 END) OVER (
                PARTITION BY date ORDER BY date) as vol_in,
            sum(CASE WHEN amount < 0 THEN amount ELSE 0 END) OVER (
                PARTITION BY date ORDER BY date) as vol_out,
            """

        # get the main query from the data prepared above
        main_query = self._get_main_query(
            journal_list, additional_subquery, report_type,
            total_initial_saldo, journals_balances, daily_volumes, group_by
        )
        self.final_query = main_query
        self.env.cr.execute(main_query)
        report_lines = self.env.cr.fetchall()

        # return the table with the output
        if self.show_table:
            complete_report = [journal_header] + [all_balances] + report_lines
            self.bank_balances = self._tuple_to_table(
                'bank', css_dict, complete_report, init_col, col_numb)
            # self.raw_table = self.bank_balances
        else:
            self.bank_balances = False

        # if the chart options is selected, show chart or empty it
        if self.show_chart:
            bokeh = self.env['ir.module.module'].search(
                [('name', '=', 'web_widget_bokeh_chart')])
            if not bokeh or bokeh.state != 'installed':
                raise UserError(_(
                    'You need to install the web_widget_bokeh_chart module '
                    'to see the graph chart! \n You can find an open PR at'
                    'this link: https://github.com/OCA/web/pull/1222.'))
        if (self.show_chart and
                not self.detailed_balance and
                len(complete_report) > 3):
            self.bank_balance_chart = self._compute_bank_chart(
                journal_header, all_balances, report_lines, init_col, col_numb)
        else:
            self.bank_balance_chart = _("""
                <p>The chart can not be visible for the following reasons:</p>
                <ul>
                    <li>You did not flag 'Show chart' parameter,</li>
                    <li>You flagged the 'Detailed balance' parameter,
                        the chart is a daily chart and details
                    can not be shown,</li>
                    <li>There are operations only in one day, please check the 
                        table and extend the date range.</li>
                </ul>
                            """)

    def _get_background_color(self, kind, line, css_dict):
        if kind == 'bank':
            return css_dict.get(line[1], False) if css_dict else ''

    def format_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, float):
            return formatLang(self.env, value, 2, monetary=True)
        elif isinstance(value, datetime.date):
            return value.strftime("%Y-%m-%d")

    def _tuple_to_table(self, kind, css_dict, complete_report,
                        init_col, col_numb):
        """This method transforms a list of tuples into an html table with
        'collapsed' details"""

        # main parameters
        prev_line = ['']
        daily_line, daily_details = '', ''
        num_parent, prev_balance, balance = 0, 0, 0
        result = "<table class='table'> \n<tr>"

        for num, line in enumerate(complete_report):
            # creating the table header and initial balance
            if num == 0:
                for head in line:
                    result += "<th>{}</th>".format(head)
                result += "\n</tr>\n<tr>"
            elif num == 1:
                daily_details = ''
                balance += sum(line[5:])
                prev_balance = balance
                for init_bal in line:
                    daily_details += "<td>{}</td>".format(
                        self.format_value(init_bal))
                daily_details += "\n</tr>"
                prev_line = line

                # if there are no report lines, we return the table
                if len(complete_report) == 2:
                    result += daily_details + "</table>"
                    return result
            else:
                style = ''

                # in detailed report, for each day we create a line with totals
                # we recognize a new day because we have a new date on the line
                if self.detailed_balance:
                    if line[0] != prev_line[0]:

                        # setting the totals for each bank
                        totals = ''
                        for numb in range(col_numb):
                            pos = numb + 5
                            totals += '<td>{}</td>'.format(prev_line[pos])

                        # we attach previous days results
                        result += daily_line.format(
                            self.format_value(balance - prev_balance),
                            self.format_value(balance), totals) + daily_details
                        daily_details = ''
                        prev_balance = balance
                        num_parent += 1

                        line_date = self.format_value(line[0])
                        daily_line = """
                            <tr style='background-color:#E8E8E8;'
                            class='collapsed' data-toggle='collapse' 
                            data-target='.parent{}Content'> <td>{}</td><td>
                            </td><td></td><td>{}</td><td>{}</td>{}<td>
                            {}</td></tr>""".format(num_parent, line_date, '{}',
                                                   '{}', '{}', line_date)
                    style = "class='collapse parent{}Content'".format(
                        num_parent)
                balance += line[3]

                # creating lines with prefix number of columns, i.e date, total
                # journals and date again. Other columns are for reporting!
                color = self._get_background_color('bank', line, css_dict)
                daily_details += "<tr style='background-color:{};' {}>".format(
                    color, style)
                col_number = init_col + col_numb + 2
                for pos in range(col_number):
                    # customizations for detailed report
                    if self.detailed_balance and pos == 0:
                        daily_details += "<td></td>"
                    elif self.detailed_balance and pos == 4:
                        daily_details += "<td>{}</td>".format(
                            self.format_value(balance))

                    # customizations for daily report
                    elif not self.detailed_balance and pos == 1:
                        vol_in = self.format_value(
                            line[pos]) if line[pos] else ''
                        daily_details += "<td>{}</td>".format(vol_in)
                    elif not self.detailed_balance and pos == 2:
                        vol_out = self.format_value(
                            line[pos]) if line[pos] else ''
                        daily_details += "<td>{}</td>".format(vol_out)

                    # all other columns are managed in the same way
                    else:
                        daily_details += "<td> {} </td>".format(
                            self.format_value(line[pos]))

                prev_line = line

                daily_details += "</tr>"

        # setting the totals for each bank
        totals = ''
        for numb in range(col_numb):
            pos = numb + 5
            totals += '<td>{}</td>'.format(prev_line[pos])

        # we include the last line of the loop
        result += daily_line.format(
            formatLang(self.env, (balance - prev_balance), 2, monetary=True),
            formatLang(self.env, balance, 2, monetary=True), totals,
            ) + daily_details

        result += "</table>"
        return result

    def compute_balance_at_date(self, journal, date, currency_id):
        """Compute bank balance for the given journal at the given date,balance
        at the beginning of the date (moves at that date are excluded)"""
        # take bank statements prior to that date
        statememt_list = self.env['account.bank.statement'].search([
            ('initial_date', '<=', date),
            ('initial_date', '<=', date),
            ('journal_id', '=', journal.id),
        ])
        balance_curr = 0.0
        if statememt_list:
            statement = statememt_list.sorted(key=lambda r: r.initial_date)[-1]
            # convert initial balance in main currency
            balance = statement.balance_start
            line_currency = statement.currency_id
            balance_curr = line_currency.compute(
                balance, currency_id)
            # from initial balance add all lines to get to the required date
            for line in statement.line_ids:
                if line.date < date:
                    balance_curr += line.amount_main_currency
        return balance_curr

    @api.multi
    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_end == "" or self.date_end < self.date_start:
            self.date_end = self.date_start

    @api.multi
    @api.onchange('forecast_options')
    def onchange_forecast_options(self):
        self.include_account_moves = False
        self.include_draft_invoices = False
        self.include_bank_fc_line = False

    @api.model
    def _get_default_journals(self):
        journal_list = self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('treasury_planning', '!=', True)
        ])
        return journal_list

    @api.multi
    def export_table(self):
        """Export table into CSV"""
        self.ensure_one()

        if not self.bank_balances:
            raise UserError(_("There is no table to export"))

        return {
            'type': 'ir.actions.act_url',
            'url': '/treasury/forecast/download/{}'.format(self.id),
            'target': 'new',
        }

    def _compute_bank_chart(self, journal_header, all_balances,
                            report_lines, init_col, col_numb):
        """Present bank balance data in a graph view"""
        from datetime import datetime
        from bokeh.plotting import figure
        from bokeh.embed import file_html
        from bokeh.resources import CDN
        from bokeh.models import ColumnDataSource, NumeralTickFormatter,\
            HoverTool, LinearAxis, Range1d
        from bokeh.palettes import viridis, GnBu3
        from math import pi

        source = {}
        # set dates in the graph
        tooltips = [('date', '@date{%F}')]
        dates = []
        for l in report_lines:
            dates.append(datetime.strptime(str(l[0]), '%Y-%m-%d'))
        source['date'] = dates

        for journal in range(col_numb + 1):
            pos = init_col + journal
            dict_key = journal_header[pos]
            string = '@{%s}' % dict_key
            tooltips.append((dict_key, string + '{0,0f}'))
            source[dict_key] = []

            for num, bkl in enumerate(report_lines):
                source[dict_key].append(bkl[pos])

        # Base line graph draw
        line_y_top = self.line_y_top or max(source['Total'])
        line_y_bottom = self.line_y_bottom or min(source['Total'])
        chart = figure(title="Bank forecast", sizing_mode='scale_width',
                       y_range=(line_y_bottom, line_y_top),
                       plot_height=self.chart_height,
                       plot_width=self.chart_width, x_axis_type='datetime',
                       toolbar_location="above")
        chart.grid.grid_line_alpha = 0.3
        chart.xaxis.axis_label = 'Date'
        chart.yaxis.axis_label = 'Amount'
        chart.yaxis[0].formatter = NumeralTickFormatter(format='0,0.')
        chart.xaxis.major_label_orientation = pi / 4

        chart.legend.location = "top_left"

        # if daily total, show bar chart with volumes
        if not self.detailed_balance:
            source.update({'date': dates, 'cash_in': [], 'cash_out': []})
            vol_total = []
            for vol in report_lines:
                source['cash_in'].append(vol[1])
                source['cash_out'].append(-vol[2])
                vol_total.append(vol[1] - vol[2])

            y_ax_height = max(vol_total) * max(0.1, self.bar_char_height)
            states = ['cash_in', 'cash_out']
            colors = ['#7daf59', '#f48342']
            chart.extra_y_ranges = \
                {"Volume": Range1d(start=0, end=y_ax_height)}
            chart.add_layout(LinearAxis(y_range_name="Volume"), 'right')
            chart.vbar_stack(states, x='date', width=self.bar_size,
                             source=ColumnDataSource(source),
                             color=colors, y_range_name="Volume")
            chart.yaxis[1].formatter = NumeralTickFormatter(format='0,0.')
            tooltips += [('cash_out', '@cash_out{0,0f}'),
                         ('cash_in', '@cash_in{0,0f}')]

        # drawing the lines, the dates used as key
        for ((key, value), color) in zip(source.items(), viridis(len(source))):
            if key not in ['date', 'cash_in', 'cash_out']:
                chart.line('date', key, source=source, line_width=1.2,
                           color=color)  # , legend=key)

        chart.legend.location = "top_left"

        chart.add_tools(HoverTool(
            tooltips=tooltips,
            formatters={'date': 'datetime', 'Total': 'numeral'},
            mode='mouse'))

        if chart:
            return file_html(chart, CDN)

        return True

    @api.onchange('default_id')
    def onchange_default_id(self):
        if self.default_id:
            self.update({
                'journal_ids': self.default_id.journal_ids,
                'detailed_balance': self.default_id.detailed_balance,
                'include_account_moves': self.default_id.include_account_moves,
                'include_draft_invoices': self.default_id.include_draft_invoices,
                'include_sale_orders': self.default_id.include_sale_orders,
                'include_bank_fc_line': self.default_id.include_bank_fc_line,

                'chart_height': self.default_id.chart_height,
                'chart_width': self.default_id.chart_width,
                'line_y_bottom': self.default_id.line_y_bottom,
                'line_y_top': self.default_id.line_y_top,
                'bar_char_height': self.default_id.bar_char_height,
                'bar_size': self.default_id.bar_size,
                'fc_css_dict': self.default_id.fc_css_dict,
                'show_table': self.default_id.show_table,
                'show_chart': self.default_id.show_chart,
            })


class BankBalanceDefault(models.Model):
    """Default configuration for treasury forecast."""
    _name = "bank.balance.configuration"
    _order = "priority"
    _description = 'Defining and setting default configuration.'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    priority = fields.Integer(string='Priority')

    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Journals', domain="[('type', '=', 'bank')]",)
    detailed_balance = fields.Boolean(string='Detailed balance')
    include_account_moves = fields.Boolean(string='Incl. account moves')
    include_draft_invoices = fields.Boolean(string='Incl. draft invoices')
    include_sale_orders = fields.Boolean(string='Incl. sale orders')
    include_bank_fc_line = fields.Boolean(string='Forec.')

    chart_height = fields.Integer('Chart Height')
    chart_width = fields.Integer('Chart Width')

    line_y_bottom = fields.Float('Bottom')
    line_y_top = fields.Float('Top')
    bar_char_height = fields.Float(string='Height')
    bar_size = fields.Float("Bar size")
    show_table = fields.Boolean(string='Show table', default=True)
    show_chart = fields.Boolean(string='Show chart', default=False)
    fc_css_dict = fields.Text(
        string='Dictionary with colours',
        default="""{
            '': '',
            'BNK': '#FFFFFF',
            'FBK': '#D4EFDF',
            'FPL': '#FAFAD2',
            'DFT': '#D7DBDD',
        }""")
