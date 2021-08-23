# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields
from datetime import datetime, timedelta
from odoo.tools.misc import format_date

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter
import io



class ReportGeneralLedger(models.AbstractModel):
    _inherit = "account.general.ledger"
    
    filter_currencys = True
        
    def _build_options(self, previous_options=None):
        res = super(ReportGeneralLedger, self)._build_options(previous_options)
        if self.filter_currencys :
            currencies = self.env['res.currency'].search([])
            res['currenciess'] = [{'id': c.id, 'name': c.name, 'selected': False} for c in currencies]
            if 'curr' in self._context:
                for c in res['currenciess']:
                    if c['id'] == self._context.get('curr'):
                        c['selected'] = True
            else:
                for c in res['currenciess']:
                    if c['id'] == self.env.user.company_id.currency_id.id:
                        c['selected'] = True
            res['currencys'] = True
        return res
    
    @api.model
    def _get_lines(self, options, line_id=None):
        res = super(ReportGeneralLedger, self)._get_lines(options, line_id)
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            if cur != self.env.user.company_id.currency_id:
                lines = []
                context = self.env.context
                company_id = self.env.user.company_id
                used_currency = cur
                dt_from = options['date'].get('date_from')
                line_id = line_id and int(line_id.split('_')[1]) or None
                aml_lines = []
                # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
                grouped_accounts = self.with_context(date_from_aml=dt_from, date_from=dt_from and company_id.compute_fiscalyear_dates(datetime.strptime(dt_from, "%Y-%m-%d"))['date_from'] or None)._group_by_account_id(options, line_id)
                sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
                unfold_all = context.get('print_mode') and len(options.get('unfolded_lines')) == 0
                for account in sorted_accounts:
                    debit = grouped_accounts[account]['debit']
                    credit = grouped_accounts[account]['credit']
                    balance = grouped_accounts[account]['balance']
                    
                    debit = cur._compute(self.env.user.company_id.currency_id,cur,debit)
                    credit = cur._compute(self.env.user.company_id.currency_id,cur,credit)
                    balance = cur._compute(self.env.user.company_id.currency_id,cur,balance)

                    amount_currency = '' if not account.currency_id else self.format_value(grouped_accounts[account]['amount_currency'], currency=account.currency_id)
                    """
                    if cur == account.currency_id:
                        amount_currency = '' if not account.currency_id else self.format_value(grouped_accounts[account]['amount_currency'], currency=self.env.user.company_id.currency_id)
                    """
                    lines.append({
                        'id': 'account_%s' % (account.id,),
                        'name': account.code + " " + account.name,
                        'columns': [{'name': v} for v in [amount_currency, self.format_value(debit,cur), self.format_value(credit,cur), self.format_value(balance,cur)]],
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': 'account_%s' % (account.id,) in options.get('unfolded_lines') or unfold_all,
                        'colspan': 4,
                    })
                    if 'account_%s' % (account.id,) in options.get('unfolded_lines') or unfold_all:
                        initial_debit = grouped_accounts[account]['initial_bal']['debit']
                        initial_credit = grouped_accounts[account]['initial_bal']['credit']
                        initial_balance = grouped_accounts[account]['initial_bal']['balance']
                        
                        initial_debit = cur._compute(self.env.user.company_id.currency_id,cur,initial_debit)
                        initial_credit = cur._compute(self.env.user.company_id.currency_id,cur,initial_credit)
                        initial_balance = cur._compute(self.env.user.company_id.currency_id,cur,initial_balance)
                        
                        initial_currency = '' if not account.currency_id else self.format_value(grouped_accounts[account]['initial_bal']['amount_currency'], currency=account.currency_id)
                        domain_lines = [{
                            'id': 'initial_%s' % (account.id,),
                            'class': 'o_account_reports_initial_balance',
                            'name': _('Initial Balance'),
                            'parent_id': 'account_%s' % (account.id,),
                            'columns': [{'name': v} for v in ['', '', '', initial_currency, self.format_value(initial_debit,cur), self.format_value(initial_credit,cur), self.format_value(initial_balance,cur)]],
                        }]
                        progress = initial_balance
                        amls = amls_all = grouped_accounts[account]['lines']
                        too_many = False
                        if len(amls) > 80 and not context.get('print_mode'):
                            amls = amls[:80]
                            too_many = True
                        for line in amls:
                            if options.get('cash_basis'):
                                line_debit = line.debit_cash_basis
                                line_credit = line.credit_cash_basis
                            else:
                                line_debit = line.debit
                                line_credit = line.credit
                                
                            line_debit = line.company_id.currency_id.compute(line_debit, used_currency)
                            line_credit = line.company_id.currency_id.compute(line_credit, used_currency)
                            progress = progress + line_debit - line_credit
                            currency = "" if not line.currency_id else self.with_context(no_format=False).format_value(cur.with_context(date=line.date)._compute(self.env.user.company_id.currency_id,cur,line.amount_currency ), currency=cur)
                            name = []
                            name = line.name and line.name or ''
                            if line.ref:
                                name = name and name + ' - ' + line.ref or line.ref
                            name_title = name
                            # Don't split the name when printing
                            if len(name) > 35 and not self.env.context.get('no_format') and not self.env.context.get('print_mode'):
                                name = name[:32] + "..."
                            partner_name = line.partner_id.name
                            partner_name_title = partner_name
                            if partner_name and len(partner_name) > 35  and not self.env.context.get('no_format') and not self.env.context.get('print_mode'):
                                partner_name = partner_name[:32] + "..."
                            caret_type = 'account.move'
                            if line.invoice_id:
                                caret_type = 'account.invoice.in' if line.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                            elif line.payment_id:
                                caret_type = 'account.payment'
                            columns = [{'name': v} for v in [format_date(self.env, line.date), name, partner_name, currency,
                                            line_debit != 0 and self.format_value(line_debit,cur) or '',
                                            line_credit != 0 and self.format_value(line_credit,cur) or '',
                                            self.format_value(progress,cur)]]
                            columns[1]['class'] = 'whitespace_print'
                            columns[2]['class'] = 'whitespace_print'
                            columns[1]['title'] = name_title
                            columns[2]['title'] = partner_name_title
                            line_value = {
                                'id': line.id,
                                'caret_options': caret_type,
                                'class': 'top-vertical-align',
                                'parent_id': 'account_%s' % (account.id,),
                                'name': line.move_id.name if line.move_id.name else '/',
                                'columns': columns,
                                'level': 4,
                            }
                            aml_lines.append(line.id)
                            domain_lines.append(line_value)
                        domain_lines.append({
                            'id': 'total_' + str(account.id),
                            'class': 'o_account_reports_domain_total',
                            'parent_id': 'account_%s' % (account.id,),
                            'name': _('Total '),
                            'columns': [{'name': v} for v in ['', '', '', amount_currency, self.format_value(debit,cur), self.format_value(credit,cur), self.format_value(balance,cur)]],
                        })
                        if too_many:
                            domain_lines.append({
                                'id': 'too_many' + str(account.id),
                                'parent_id': 'account_%s' % (account.id,),
                                'name': _('There are more than 80 items in this list, click here to see all of them'),
                                'colspan': 7,
                                'columns': [{}],
                                'action': 'view_too_many',
                                'action_id': 'account,%s' % (account.id,),
                            })
                        lines += domain_lines
        
                journals = [j for j in options.get('journals') if j.get('selected')]
                if len(journals) == 1 and journals[0].get('type') in ['sale', 'purchase'] and not line_id:
                    total = self._get_journal_total()
                    lines.append({
                        'id': 0,
                        'class': 'total',
                        'name': _('Total'),
                        'columns': [{'name': v} for v in ['', '', '', '', self.format_value(total['debit'],cur), self.format_value(total['credit'],cur), self.format_value(total['balance'],cur)]],
                        'level': 1,
                        'unfoldable': False,
                        'unfolded': False,
                    })
                    lines.append({
                        'id': 0,
                        'name': _('Tax Declaration'),
                        'columns': [{'name': v} for v in ['', '', '', '', '', '', '']],
                        'level': 1,
                        'unfoldable': False,
                        'unfolded': False,
                    })
                    lines.append({
                        'id': 0,
                        'name': _('Name'),
                        'columns': [{'name': v} for v in ['', '', '', '', _('Base Amount'), _('Tax Amount'), '']],
                        'level': 2,
                        'unfoldable': False,
                        'unfolded': False,
                    })
                    journal_currency = self.env['account.journal'].browse(journals[0]['id']).company_id.currency_id
                    for tax, values in self._get_taxes(journals[0]).items():
                        base_amount = journal_currency.compute(values['base_amount'], used_currency)
                        tax_amount = journal_currency.compute(values['tax_amount'], used_currency)
                        lines.append({
                            'id': '%s_tax' % (tax.id,),
                            'name': tax.name + ' (' + str(tax.amount) + ')',
                            'caret_options': 'account.tax',
                            'unfoldable': False,
                            'columns': [{'name': v} for v in [self.format_value(base_amount), self.format_value(tax_amount), '']],
                            'colspan': 5,
                            'level': 4,
                        })
        
                if self.env.context.get('aml_only', False):
                    return aml_lines
                return lines
        return res
    
    def get_pdf(self, options, minimal_layout=True):
        for opt in options['currenciess']:
            if opt['selected'] and self.env['res.currency'].browse(opt['id']) != self.env.user.company_id.currency_id:
                return super(ReportGeneralLedger, self.with_context(curr = opt['id'])).get_pdf(options,minimal_layout)
        return super(ReportGeneralLedger, self).get_pdf(options,minimal_layout)
    
    def get_xlsx(self, options, response):
        for opt in options['currenciess']:
            if opt['selected'] and self.env['res.currency'].browse(opt['id']) != self.env.user.company_id.currency_id:
                return super(ReportGeneralLedger, self.with_context(curr = opt['id'])).get_xlsx(options,response)
        return super(ReportGeneralLedger, self).get_xlsx(options,response)

   