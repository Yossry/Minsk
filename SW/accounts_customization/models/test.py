from odoo import api, fields, models, tools,_
from odoo.exceptions import except_orm, ValidationError ,UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta , date
import math
# from num2words import num2words
from odoo.exceptions import Warning
from odoo.tools import float_utils, float_compare ,pycompat ,email_re, email_split, email_escape_char, float_is_zero, date_utils

from odoo.tools.misc import format_date





# class respartnerUpdate(models.Model):
#     _inherit = "res.partner"
    
#     sequence_no = fields.Char('Partner No', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'),track_visibility="onchange")
    

#     @api.model_create_multi
#     def create(self, vals_list):
           
#         if self.env.context.get('import_file'):
#             self._check_import_consistency(vals_list)
#         for vals in vals_list:
#             if vals.get('sequence_no', _('New')) == _('New'):
#                 vals['sequence_no'] = self.env['ir.sequence'].next_by_code('res.partner') or 'New'
#             if vals.get('website'):
#                 vals['website'] = self._clean_website(vals['website'])
#             if vals.get('parent_id'):
#                 vals['company_name'] = False
#             # compute default image in create, because computing gravatar in the onchange
#             # cannot be easily performed if default images are in the way
#             if not vals.get('image'):
#                 vals['image'] = self._get_default_image(vals.get('type'), vals.get('is_company'), vals.get('parent_id'))
#             tools.image_resize_images(vals, sizes={'image': (1024, None)})
#         partners = super(respartnerUpdate, self).create(vals_list)

#         # channel_all_employees = self.env.ref('accounts_customization.channel_all_new_customer').read()[0]
#         # template_new_employee = self.env.ref('accounts_customization.email_template_data_new_customer').read()[0]
#         # # raise ValidationError(_(template_new_employee))
#         # if template_new_employee:
#         #     # MailTemplate = self.env['mail.template']
#         #     body_html = template_new_employee['body_html']
#         #     subject = template_new_employee['subject']
#         #     # raise ValidationError(_('%s %s ') % (body_html,subject))
#         #     ids = channel_all_employees['id']
#         #     channel_id = self.env['mail.channel'].search([('id', '=', ids)])
#         #     body = """Hello, there are New Customer Added to customer lists with name %s and code %s"""% (vals['name'],vals['sequence_no'])
#         #     channel_id.message_post(body=body, subject='New Customer Added',subtype='mail.mt_comment')
        

#         if self.env.context.get('_partners_skip_fields_sync'):
#             return partners

#         for partner, vals in pycompat.izip(partners, vals_list):
#             partner._fields_sync(vals)
#             partner._handle_first_contact_creation()
#         return partners

#     @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name')
#     def _compute_display_name(self):
#         diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=False, show_code=False)
#         names = dict(self.with_context(**diff).name_get())
#         for partner in self:
#             partner.display_name = names.get(partner.id)

#     def _get_name(self):
#         """ Utility method to allow name_get to be overrided without re-browse the partner """
#         partner = self
#         name = partner.name

#         if partner.company_name or partner.parent_id:
#             if not name and partner.type in ['invoice', 'delivery', 'other']:
#                 name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
#             if not partner.is_company:
#                 name = "%s ,%s" % (partner.commercial_company_name or partner.parent_id.name,name)
            
#         if self._context.get('show_address_only'):
#             name = partner._display_address(without_company=True)
#         if self._context.get('show_address'):
#             name = name + "\n" + partner._display_address(without_company=True)
#         name = name.replace('\n\n', '\n')
#         name = name.replace('\n\n', '\n')
#         if self._context.get('address_inline'):
#             name = name.replace('\n', ', ')
#         if self._context.get('show_email') and partner.email:
#             name = "%s <%s>" % (name, partner.email)
#         if self._context.get('show_code') and partner.sequence_no:
#             name = "%s - %s" % (name, partner.sequence_no)
#         if self._context.get('html_format'):
#             name = name.replace('\n', '<br/>')
#         if self._context.get('show_vat') and partner.vat:
#             name = "%s ‒ %s" % (name, partner.vat)
#         return name

# Ledger Report Updates




# class AccountReportcus(models.AbstractModel):
#     _inherit = 'account.report'

#     @api.multi
#     def get_html(self, options, line_id=None, additional_context=None):
#         '''
#         return the html value of report, or html value of unfolded line
#         * if line_id is set, the template used will be the line_template
#         otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
#         we don't want to reload all lines, just get the one we unfolded.
#         '''
#         # Check the security before updating the context to make sure the options are safe.
#         self._check_report_security(options)

#         # Prevent inconsistency between options and context.
#         self = self.with_context(self._set_context(options))

#         templates = self._get_templates()
#         report_manager = self._get_report_manager(options)
#         report = {'name': self._get_report_name(),
#                 'summary': report_manager.summary,
#                 'company_name': self.env.user.company_id.name,
#                 'yo_date': date.today(),
#                 'company_zip': self.env.user.company_id.zip,
#                 'company_street': self.env.user.company_id.street,
#                 'company_currency': self.env.user.company_id.currency_id.name,
#                 'company_currencylabel': self.env.user.company_id.currency_id.currency_unit_label,
#                 'company_tel': self.env.user.company_id.phone,
#                 }
#         lines = self._get_lines(options, line_id=line_id)

#         if options.get('hierarchy'):
#             lines = self._create_hierarchy(lines)

#         footnotes_to_render = []
#         if self.env.context.get('print_mode', False):
#             # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
#             # we don't know all the visible lines.
#             footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
#             number = 0
#             for line in lines:
#                 f = footnotes.get(str(line.get('id')))
#                 if f:
#                     number += 1
#                     line['footnote'] = str(number)
#                     footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

#         rcontext = {'report': report,
#                     'lines': {'columns_header': self.get_header(options), 'lines': lines},
#                     'options': options,
#                     'context': self.env.context,
#                     'model': self,
#                 }
#         if additional_context and type(additional_context) == dict:
#             rcontext.update(additional_context)
#         if self.env.context.get('analytic_account_ids'):
#             rcontext['options']['analytic_account_ids'] = [
#                 {'id': acc.id, 'name': acc.name} for acc in self.env.context['analytic_account_ids']
#             ]

#         render_template = templates.get('main_template', 'acc_pi.main_template')
#         if line_id is not None:
#             render_template = templates.get('line_template', 'acc_pi.line_template')
#         html = self.env['ir.ui.view'].render_template(
#             render_template,
#             values=dict(rcontext),
#         )
#         if self.env.context.get('print_mode', False):
#             for k,v in self._replace_class().items():
#                 html = html.replace(k, v)
#             # append footnote as well
#             html = html.replace(b'<div class="js_account_report_footnotes"></div>', self.get_html_footnotes(footnotes_to_render))
#         return html

    
#     def get_report_informations(self, options):
#         '''
#         return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
#         '''
#         options = self._get_options(options)
#         # apply date and date_comparison filter
#         self._apply_date_filter(options)

#         searchview_dict = {'options': options, 'context': self.env.context}
#         # Check if report needs analytic
#         if options.get('analytic_accounts') is not None:
#             searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
#             options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
#         if options.get('analytic_tags') is not None:
#             searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
#             options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
#         if options.get('partner'):
#             options['selected_partner_ids'] = [str(self.env['res.partner'].browse(int(partner)).name) +' ,  '+ str(self.env['res.partner'].browse(int(partner)).sequence_no) for partner in options['partner_ids']]
#             options['partner_zip'] = [self.env['res.partner'].browse(int(partner)).zip for partner in options['partner_ids']]
#             options['partner_code'] = [self.env['res.partner'].browse(int(partner)).sequence_no for partner in options['partner_ids']]
#             options['selected_phone'] = [self.env['res.partner'].browse(int(partner)).phone for partner in options['partner_ids']]
#             options['selected_street'] = [self.env['res.partner'].browse(int(partner)).street for partner in options['partner_ids']]
#             options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

#         # Check whether there are unposted entries for the selected period or not (if the report allows it)
#         if options.get('date') and options.get('all_entries') is not None:
#             date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
#             period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
#             options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

#         report_manager = self._get_report_manager(options)
#         info = {'options': options,
#                 'context': self.env.context,
#                 'report_manager_id': report_manager.id,
#                 'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
#                 'buttons': self._get_reports_buttons(),
#                 'main_html': self.get_html(options),
#                 'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
#                 }
#         return info





# class ReportPartnerLedgercus(models.AbstractModel):
#     _inherit = "account.partner.ledger"

#     @api.model
#     def _get_report_name(self):
#         return _('STATEMENT OF ACCOUNTS')

#     def _get_columns_name(self, options):
#         columns = [
#             {},
#             {'name': _('JRNL')},
#             {'name': _('Account')},
#             {'name': _('Ref')},
#             {'name': _('Project Name')},
#             {'name': _('Due Date'), 'class': 'date'},
#             {'name': _('Days')},
#             {'name': _('Matching Number')},
#             {'name': _('Initial Balance'), 'class': 'number'},
#             {'name': _('Debit'), 'class': 'number'},
#             {'name': _('Credit'), 'class': 'number'}]

#         if self.user_has_groups('base.group_multi_currency'):
#             columns.append({'name': _('Amount Currency'), 'class': 'number'})

#         columns.append({'name': _('Balance'), 'class': 'number'})
        

#         return columns


#     @api.model
#     def _get_lines(self, options, line_id=None):
#         offset = int(options.get('lines_offset', 0))
#         lines = []
#         context = self.env.context
#         company_id = context.get('company_id') or self.env.user.company_id
#         if line_id:
#             line_id = int(line_id.split('_')[1]) or None
#         elif options.get('partner_ids') and len(options.get('partner_ids')) == 1:
#             #If a default partner is set, we only want to load the line referring to it.
#             partner_id = options['partner_ids'][0]
#             line_id = partner_id
#         if line_id:
#             if 'partner_' + str(line_id) not in options.get('unfolded_lines', []):
#                 options.get('unfolded_lines', []).append('partner_' + str(line_id))

#         grouped_partners = self._group_by_partner_id(options, line_id)
#         sorted_partners = sorted(grouped_partners, key=lambda p: p.name or '')
#         unfold_all = context.get('print_mode') and not options.get('unfolded_lines')
#         total_initial_balance = total_debit = total_credit = total_balance = 0.0
#         for partner in sorted_partners:
#             debit = grouped_partners[partner]['debit']
#             credit = grouped_partners[partner]['credit']
#             balance = grouped_partners[partner]['balance']
#             initial_balance = grouped_partners[partner]['initial_bal']['balance']
#             total_initial_balance += initial_balance
#             total_debit += debit
#             total_credit += credit
#             total_balance += balance
#             days = 'days'
#             columns = [self.format_value(initial_balance), self.format_value(debit), self.format_value(credit)]
#             if self.user_has_groups('base.group_multi_currency'):
#                 columns.append('')
#             columns.append(self.format_value(balance))
            
#             # don't add header for `load more`
#             if offset == 0:
#                 lines.append({
#                     'id': 'partner_' + str(partner.id),
#                     'name': partner.name,
#                     'columns': [{'name': v} for v in columns],
#                     'level': 2,
#                     'trust': partner.trust,
#                     'unfoldable': True,
#                     'unfolded': 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all,
#                     'colspan': 8,
#                 })
#             user_company = self.env.user.company_id
#             used_currency = user_company.currency_id
#             if 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all:
#                 if offset == 0:
#                     progress = initial_balance
#                 else:
#                     progress = float(options.get('lines_progress', initial_balance))
#                 domain_lines = []
#                 amls = grouped_partners[partner]['lines']

#                 remaining_lines = 0
#                 if not context.get('print_mode'):
#                     remaining_lines = grouped_partners[partner]['total_lines'] - offset - len(amls)

#                 for line in amls:
#                     if options.get('cash_basis'):
#                         line_debit = line.debit_cash_basis
#                         line_credit = line.credit_cash_basis
#                     else:
#                         line_debit = line.debit
#                         line_credit = line.credit
#                     date = amls.env.context.get('date') or fields.Date.today()
#                     line_currency = line.company_id.currency_id
#                     line_debit = line_currency._convert(line_debit, used_currency, user_company, date)
#                     line_credit = line_currency._convert(line_credit, used_currency, user_company, date)
#                     progress_before = progress
#                     progress = progress + line_debit - line_credit
#                     caret_type = 'account.move'
#                     if line.invoice_id:
#                         caret_type = 'account.invoice.in' if line.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
#                     elif line.payment_id:
#                         caret_type = 'account.payment'

#                     if line.invoice_id:
#                         if line.invoice_id.project:
#                             project_name = """[%s]%s""" % (line.invoice_id.project.code,line.invoice_id.project.name)
#                         else:
#                             project_name = ''
#                     else:
#                         if line.analytic_account_id.code or line.analytic_account_id.name:
#                             project_name = ''
#                             project_name = """[%s]%s""" % (line.analytic_account_id.code,line.analytic_account_id.name)
#                         else:
#                             project_name = ''
#                     days =  (line.date_maturity - line.move_id.date).days
#                     domain_columns = [line.journal_id.code, line.account_id.code,self._format_aml_name(line),project_name, 
#                                       line.date_maturity and format_date(self.env, line.date_maturity) or '',days,
#                                       line.full_reconcile_id.name or '', self.format_value(progress_before),
#                                       line_debit != 0 and self.format_value(line_debit) or '',
#                                       line_credit != 0 and self.format_value(line_credit) or '']
#                     if self.user_has_groups('base.group_multi_currency'):
#                         domain_columns.append(self.with_context(no_format=False).format_value(line.amount_currency, currency=line.currency_id) if line.amount_currency != 0 else '')
#                     domain_columns.append(self.format_value(progress))
#                     columns = [{'name': v} for v in domain_columns]
#                     columns[3].update({'class': 'date'})
#                     domain_lines.append({
#                         'id': line.id,
#                         'parent_id': 'partner_' + str(partner.id),
#                         'name': format_date(self.env, line.date),
#                         'class': 'date',
#                         'columns': columns,
#                         'caret_options': caret_type,
#                         'level': 4,
#                     })

#                 # load more
#                 if remaining_lines > 0:
#                     domain_lines.append({
#                         'id': 'loadmore_%s' % partner.id,
#                         'offset': offset + self.MAX_LINES,
#                         'progress': progress,
#                         'class': 'o_account_reports_load_more text-center',
#                         'parent_id': 'partner_%s' % partner.id,
#                         'name': _('Load more... (%s remaining)') % remaining_lines,
#                         'colspan': 10 if self.user_has_groups('base.group_multi_currency') else 9,
#                         'columns': [{}],
#                     })
#                 lines += domain_lines

#         if not line_id:
#             total_columns = ['', '', '', '', '','', '', self.format_value(total_initial_balance), self.format_value(total_debit), self.format_value(total_credit)]
#             if self.user_has_groups('base.group_multi_currency'):
#                 total_columns.append('')
#             total_columns.append(self.format_value(total_balance))
#             lines.append({
#                 'id': 'grouped_partners_total',
#                 'name': _('Total'),
#                 'level': 0,
#                 'class': 'o_account_reports_domain_total',
#                 'columns': [{'name': v} for v in total_columns],
#             })
#         return lines








# # Accounts Customization Part
class AccountInvoiceRefundCus(models.TransientModel):
    _inherit = 'account.invoice.refund'

    date_invoice = fields.Date(string='Debit Note Date', default=fields.Date.context_today, required=True)
    filter_refund = fields.Selection([('refund', 'Create a draft debit note'), ('cancel', 'Cancel: create debit note and reconcile'), ('modify', 'Modify: create debit note, reconcile and create a new draft invoice')],default='refund', string='Credit Method', required=True, help='Choose how you want to credit this invoice. You cannot Modify and Cancel if the invoice is already reconciled')

# class AccountInvoiceCust(models.Model):
#     _inherit = 'account.invoice'

#     term = fields.Many2one('bank.details',string='Bank Details')
#     LPO = fields.Char('LPO No.')
#     project_name = fields.Char('Event')
#     text = fields.Char('Price in Text',compute="_com_price2",invisible=True)
#     project = fields.Many2one('account.analytic.account',string="project")
#     document_count = fields.Integer(compute='_document_count', string='# Documents')
#     comment = fields.Text('Additional Information')
    
# #     @api.model
# #     def _default_commentt(self,vals):
# #         # picking_type_id = self._context.get('default_picking_type_id')
# #         if self.type != ['in_invoice','out_refund','in_refund']:
# #             return """Terms and Conditions:
# # Goods will remain the property of MARCOMS until payment of this invoice is settled in full.
# # Cheque Payments should be made under the name of "MARCOMS LLC".
# # Official receipt should be obtained for cash payments."""
# #         else:
# #             return " "

#     @api.model
#     def create(self, vals):
#         if not vals.get('journal_id') and vals.get('type'):
#             vals['journal_id'] = self.with_context(type=vals.get('type'))._default_journal().id

#         if vals.get('type') != ['in_invoice','out_refund','in_refund']:
#             vals['comment'] = """Terms and Conditions:
# Goods will remain the property of MARCOMS until payment of this invoice is settled in full.
# Cheque Payments should be made under the name of "MARCOMS LLC".
# Official receipt should be obtained for cash payments."""
#         # else:
#         #     return " "

#         onchanges = self._get_onchange_create()
#         for onchange_method, changed_fields in onchanges.items():
#             if any(f not in vals for f in changed_fields):
#                 invoice = self.new(vals)
#                 getattr(invoice, onchange_method)()
#                 for field in changed_fields:
#                     if field not in vals and invoice[field]:
#                         vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)

#         invoice = super(AccountInvoiceCust, self.with_context(mail_create_nolog=True)).create(vals)

#         if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
#             invoice.compute_taxes()

#         return invoice

#     @api.multi
#     def _document_count(self):
#         for each in self:
#             document_ids = self.env['account.invoice.document'].sudo().search([('pay_ref', '=', each.id)])
#             each.document_count = len(document_ids)

#     @api.multi
#     def document_view(self):
#         self.ensure_one()
#         domain = [('pay_ref', '=', self.id)]
#         return {
#             'name': _('Documents'),
#             'domain': domain,
#             'res_model': 'account.invoice.document',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'tree,form',
#             'view_type': 'form',
#             'help': _('''<p class="oe_view_nocontent_create">
#                            Click to Create New Documents
#                         </p>'''),
#             'limit': 80,
#             'context': "{'default_pay_ref': '%s'}" % self.id
#         }

#     @api.depends('amount_total','currency_id')
#     def _com_price2(self):
#         for rec in self:
#         # res = super(pur_order_inherit, self)._onchange_amount()
#             rec.text = rec.currency_id.amount_to_text(rec.amount_total) if rec.currency_id else ''
#             rec.text = rec.text.replace(' And ', ' ').replace(',',' ')
#         #self.text = self.text.replace(' Dirham ', ' ')



counter_array = []
class AccountpaymentCust(models.Model):
    _inherit = 'account.payment'

    text = fields.Char('Price in Text',compute="_com_price2",invisible=True)
    # cheque_date = fields.Date('Cheque Date')
    remarks = fields.Text('Remarks')
    # seal = fields.Boolean('Include Company Seal',default=False)
    pdc_account = fields.Many2one('account.account',string="PDC Account")
    release_count = fields.Integer('Count',default=0,copy=False)
    move_relase_id = fields.Integer('Move id')
    move_entry_id = fields.Integer('Move id')
    release_check = fields.Boolean('Is Release',default=False)
    # variance_id = fields.One2many('payment.variance.inv','payment_ids',string="Payment Variance")
    variance_count = fields.Integer('Count',default=0,copy=False)
    add_variance_count = fields.Integer('Count',default=0,copy=False)
    var_account = fields.Many2one('account.account',string="Variance Account")
    var_amount = fields.Float(string="Variance Amount",compute='_var_amount')
    invoice_lines_outstand = fields.One2many('payment.invoice.line.outstand', 'payment_id', string="Outstanding Line")
    accountname = fields.Many2one('account.account',string='account')
    company_id = fields.Many2one('res.company', string='Company', change_default=True,required=True, readonly=True, states={'draft': [('readonly', False)]},default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    flag_acc = fields.Boolean('Flag',default=False)
    # prepare = fields.Char('Prepared by')
    # checked = fields.Char('Checked by')
    # received = fields.Char('Received by')
    # approved = fields.Char('Approved by')
    # verified = fields.Char('Verified by')
    
    @api.multi
    @api.depends('invoice_lines','amount','invoice_lines_outstand')
    def _var_amount(self):
        for rec in self:
            y = 0.0
            z = 0.0
            amt = rec.amount
            for x in rec.invoice_lines:
                y = y + x.allocation
            if rec.invoice_lines_outstand:
                for l in rec.invoice_lines_outstand:
                    if l.allocation:
                        z = z + l.allocation
                amt = amt + z
            rec.var_amount = amt - y

    @api.onchange('amount','currency_id')
    def _onchange_amount(self):
        res = super(AccountpaymentCust, self)._onchange_amount()
        self.check_amount_in_words = self.currency_id.amount_to_text(self.amount) if self.currency_id else ''
        self.check_amount_in_words = self.check_amount_in_words.replace(' Dirham ', ' ').replace(' Dirham',' ').replace(' And ',' ')

        return res

    @api.depends('amount','currency_id')
    def _com_price2(self):
        for rec in self:
        # res = super(pur_order_inherit, self)._onchange_amount()
            rec.text = rec.currency_id.amount_to_text(rec.amount) if rec.currency_id else ''
            rec.text = rec.text.replace(' And ', ' ').replace(',',' ').replace(' Dirham ',' ').replace(' Fils',' ').replace(' Dirham',' ')
            # rec.check_amount_in_words = rec.check_amount_in_words.replace(' Dirham ', ' ').replace(' Dirham',' ')

    

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        if self.payment_method_code == 'pdc':
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        else:
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

    
        move = self.env['account.move'].create(self._get_move_vals())
        self.move_entry_id = move.id

        ino = self.env['account.invoice']
        flag_accc = False
        # raise ValidationError(_('test'))
        if len(self.invoice_ids) != 1:
            flag_accc = True
            if self.var_amount != 0:
                amt = 0.0
                # for l in self.invoice_lines:
                    # if l.allocation :
                
                # if self.payment_method_code == 'pdc':
                # debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.effective_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
                # else:
                # debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        for l in self.invoice_lines:
                            if l.allocation:
                                
                                amt = l.allocation
                                amountss = -amt
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(debit,credit, amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml_dict.update({'date_maturity': self.payment_date})
                            # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                # raise ValidationError(_(counterpart_aml_dict))
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)

                    else:
                        if self.var_amount != 0:
                            for l in self.invoice_lines:
                                if l.allocation:
                                    
                                    amt = l.allocation
                                    amountss = -amt
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                    # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                            # raise ValidationError(_(counterpart_aml_dict))
                        else:
                            for l in self.invoice_lines:
                                if l.allocation:
                                    
                                    amt = l.allocation
                                    amountss = -amt
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals( debit,credit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                    # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                        # raise ValidationError(_(counterpart_aml_dict))
                else:
                    if self.partner_type == 'customer':
                        for l in self.invoice_lines:
                            if l.allocation:
                                
                                amt = l.allocation
                                amountss = -amt
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)
                        # raise ValidationError(_(counterpart_aml_dict))
                    else:
                        for l in self.invoice_lines:
                            if l.allocation:
                               
                                amt = l.allocation
                                amountss = -amt
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(credit,debit,  amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)
                                # raise ValidationError(_(counterpart_aml_dict))
            #Write line corresponding to invoice payment
            else:
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        for l in self.invoice_lines:
                            if l.allocation:
                                
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(debit,credit, amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml_dict.update({'date_maturity': self.payment_date})
                            # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)
                    else:
                        if self.var_amount != 0:
                            for l in self.invoice_lines:
                                if l.allocation:
                                    
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                    # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
                        else:
                            for l in self.invoice_lines:
                                if l.allocation:
                                    
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                    # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
                else:
                    if self.partner_type == 'customer':
                        for l in self.invoice_lines:
                            if l.allocation:
                                
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)
                        # raise ValidationError(_(counterpart_aml_dict))
                    else:
                        for l in self.invoice_lines:
                            if l.allocation:
                                
                                if self.payment_method_code == 'pdc':
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                else:
                                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                counterpart_aml_dict = self._get_shared_move_line_vals(credit,debit,  amount_currency, move.id, False)
                                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                counterpart_aml_dict.update({'currency_id': currency_id})
                                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                com = ino.search([('number','=',l.invoice)])
                                com.register_payment(counterpart_aml)
                                # raise ValidationError(_(counterpart_aml_dict))
        else:
            invoice_namm = ''
            amtss = 0.0
            if self.invoice_lines:
                flag_accc = True
                for l in self.invoice_lines:
                    invoice_namm = l.invoice
                    if l.allocation:
                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                        if self.var_amount != 0:
                            if self.payment_method_code == 'pdc':
                                if self.partner_type == 'customer':
                                    # for l in self.invoice_lines:
                                        # if l.allocation:
                                            
                                        amt = l.allocation
                                        amountss = -amt
                                        if self.payment_method_code == 'pdc':
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                        else:
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                        counterpart_aml_dict = self._get_shared_move_line_vals(debit,credit, amount_currency, move.id, False)
                                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                        counterpart_aml_dict.update({'currency_id': currency_id})
                                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                        # raise ValidationError(_(counterpart_aml_dict))
                                    # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                        com = ino.search([('number','=',l.invoice)])
                                        com.register_payment(counterpart_aml)

                                else:
                                    if self.var_amount != 0:
                                        # for l in self.invoice_lines:
                                        #     if l.allocation:
                                                
                                        amt = l.allocation
                                        amountss = -amt
                                        if self.payment_method_code == 'pdc':
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                        else:
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                        counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                        counterpart_aml_dict.update({'currency_id': currency_id})
                                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                        # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                        com = ino.search([('number','=',l.invoice)])
                                        com.register_payment(counterpart_aml)
                                        # raise ValidationError(_(counterpart_aml_dict))
                                    else:
                                        # for l in self.invoice_lines:
                                            # if l.allocation:
                                                
                                        amt = l.allocation
                                        amountss = -amt
                                        if self.payment_method_code == 'pdc':
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                        else:
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                        counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                        counterpart_aml_dict.update({'currency_id': currency_id})
                                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                        # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                        com = ino.search([('number','=',l.invoice)])
                                        com.register_payment(counterpart_aml)
                                        # raise ValidationError(_(counterpart_aml_dict))
                            else:
                                if self.partner_type == 'customer':
                                    # for l in self.invoice_lines:
                                    #     if l.allocation:
                                            
                                    amt = l.allocation
                                    amountss = -amt
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
                                else:
                                    # for l in self.invoice_lines:
                                    #     if l.allocation:
                                        
                                    amt = l.allocation
                                    amountss = -amt
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amountss, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals(credit,debit,  amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
                    #Write line corresponding to invoice payment
                        else:
                            if self.payment_method_code == 'pdc':
                                if self.partner_type == 'customer':
                                    # for l in self.invoice_lines:
                                    #     if l.allocation:
                                            
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals(debit,credit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                else:
                                    if self.var_amount != 0:
                                        # for l in self.invoice_lines:
                                        #     if l.allocation:
                                                
                                        if self.payment_method_code == 'pdc':
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                        else:
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                        counterpart_aml_dict = self._get_shared_move_line_vals( credit,debit, amount_currency, move.id, False)
                                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                        counterpart_aml_dict.update({'currency_id': currency_id})
                                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                        # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                        com = ino.search([('number','=',l.invoice)])
                                        com.register_payment(counterpart_aml)
                                        # raise ValidationError(_(counterpart_aml_dict))
                                    else:
                                        # for l in self.invoice_lines:
                                        #     if l.allocation:
                                                
                                        if self.payment_method_code == 'pdc':
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                        else:
                                            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                        counterpart_aml_dict = self._get_shared_move_line_vals( debit,credit, amount_currency, move.id, False)
                                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                        counterpart_aml_dict.update({'currency_id': currency_id})
                                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                                        # counterpart_aml_dict.update({'account_id': self.pdc_account.id})
                                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                        com = ino.search([('number','=',l.invoice)])
                                        com.register_payment(counterpart_aml)
                                        # raise ValidationError(_(counterpart_aml_dict))
                            else:
                                if self.partner_type == 'customer':
                                    # for l in self.invoice_lines:
                                    #     if l.allocation:
                                            
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
                                else:
                                    # for l in self.invoice_lines:
                                    #     if l.allocation:
                                            
                                    if self.payment_method_code == 'pdc':
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)
                                    else:
                                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-l.allocation, self.currency_id, self.company_id.currency_id)

                                    counterpart_aml_dict = self._get_shared_move_line_vals(credit,debit,  amount_currency, move.id, False)
                                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(l.invoice))
                                    counterpart_aml_dict.update({'currency_id': currency_id})
                                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                                    com = ino.search([('number','=',l.invoice)])
                                    com.register_payment(counterpart_aml)
                                    # raise ValidationError(_(counterpart_aml_dict))
            else:
                if self.payment_method_code == 'pdc':
                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
                else:
                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        # if self.invoice_ids:
                        #     self.invoice_ids.register_payment(counterpart_aml)
                    else:
                        counterpart_aml_dict = self._get_shared_move_line_vals( debit,credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        # raise ValidationError(_(counterpart_aml_dict))
                        # if self.invoice_ids:
                        #     self.invoice_ids.register_payment(counterpart_aml)

                else:
                    if self.partner_type == 'customer':
                        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        # if self.invoice_ids:
                        #     self.invoice_ids.register_payment(counterpart_aml)
                        # raise ValidationError(_(counterpart_aml_dict))
                    else:
                        counterpart_aml_dict = self._get_shared_move_line_vals( debit,credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'date_maturity': self.payment_date})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        # raise ValidationError(_(counterpart_aml_dict))
                        # if self.invoice_ids:
                        #     self.invoice_ids.register_payment(counterpart_aml)
                        # raise ValidationError(_(counterpart_aml_dict))


        if self.payment_method_code == 'pdc':
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        else:
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            # raise ValidationError(_(self.payment_difference))
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
            # raise ValidationError(_(counterpart_aml))

        #Write counterpart lines
        if len(self.invoice_ids) != 1:
            if not self.currency_id.is_zero(self.amount):
                
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit,debit,  -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                else:
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit,debit,  -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
        else:
            if not self.currency_id.is_zero(self.amount):
                if not self.currency_id != self.company_id.currency_id:
                    amount_currency = 0
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                    else: 
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                else:
                    if self.partner_type == 'customer':
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)
                        # raise ValidationError(_(liquidity_aml_dict))
                    else: 
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'date_maturity': self.payment_date})
                        aml_obj.create(liquidity_aml_dict)

        


    # ####################################################################################################
    # ####################################################################################################

        # if len(self.invoice_ids) != 1:
        if self.invoice_lines:
            if self.invoice_lines_outstand:
                y = 0.0
                for com in self.invoice_lines_outstand:
                    if com.allocation:
                        y = y + com.allocation

                for com in self.invoice_lines_outstand:
                    if com.allocation:
                        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(-com.allocation, self.currency_id, self.company_id.currency_id)
                        if self.partner_type == 'customer':
                            counterpart_aml_dict = self._get_shared_move_line_vals(credit,debit,  amount_currency, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                            counterpart_aml_dict.update({'currency_id': currency_id})
                            counterpart_aml_dict.update({'date_maturity': self.payment_date})
                            counterpart_amls = aml_obj.create(counterpart_aml_dict)
                            
                            partial_rec = self.env['account.partial.reconcile']
                            aml_model = self.env['account.move.line']

                            created_lines = self.env['account.move.line']
                            com.move_id.amount_residual = com.allocation
                            #reconcile all aml_to_fix
                            value = {'id':counterpart_amls.id,'m_id':com.move_id.id}
                            counter_array.append(value)
                            partial_rec |= partial_rec.create(
                                partial_rec._prepare_exchange_diff_partial_reconcile(
                                        aml=com.move_id,
                                        line_to_reconcile=counterpart_amls,
                                        currency=com.move_id.currency_id or False)
                            )
                            created_lines |= counterpart_amls
                            
                        else: 
                            counterpart_aml_dict = self._get_shared_move_line_vals( debit,credit, amount_currency, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.communication))
                            counterpart_aml_dict.update({'currency_id': currency_id})
                            counterpart_aml_dict.update({'date_maturity': self.payment_date})
                            counterpart_amls = aml_obj.create(counterpart_aml_dict)
                            # value = {'id':counterpart_amls.id}
                            # counter_array.append(value)
                            partial_rec = self.env['account.partial.reconcile']
                            aml_model = self.env['account.move.line']

                            created_lines = self.env['account.move.line']
                            com.move_id.amount_residual = com.allocation
                            #reconcile all aml_to_fix
                            value = {'id':counterpart_amls.id,'m_id':com.move_id.id}
                            counter_array.append(value)
                            partial_rec |= partial_rec.create(
                                partial_rec._prepare_exchange_diff_partial_reconcile(
                                        aml=com.move_id,
                                        line_to_reconcile=counterpart_amls,
                                        currency=com.move_id.currency_id or False)
                            )
                            created_lines |= counterpart_amls
        # #################################################################################################3
        # #################################################################################################3

        # ######################################################################################################
        # #####################################################################################################
        if self.invoice_lines  or self.flag_acc == True or (self.var_amount and flag_accc):
            if self.var_account:
                # rec.write({'state': 'draft'})
                id_account = self.var_account.id
                # aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
                # com = self.env['payment.variance.inv'].search([('payment_ids','=',rec.id)])
                # y = 0.0
                amt = 0.0
                # for x in com:
                #     y = y + x.var_amount
                #     amt = amt + x.invoice_amount
                amounts = self.var_amount
                for l in self.invoice_lines:
                    if l.allocation :
                        amt = amt + l.total_amount
                total_amt = amt
                # raise ValidationError(_('Testsss'))
                invoice_la = 'Variance Amount'
                if amounts != 0:

                    debits, credits, amount_currencys, currency_ids = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amounts, self.currency_id, self.company_id.currency_id)

                    if amounts > 0:
                        #Write line corresponding to invoice payment

                        if self.partner_type == 'customer':
                            counterpart_aml_dict = self._get_shared_move_line_vals(credits,debits,  amount_currencys, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                            counterpart_aml_dict.update({'currency_id': currency_ids})
                            counterpart_aml_dict.update({'account_id': id_account})
                            if self.payment_method_code == 'pdc':
                                counterpart_aml_dict.update({'date': self.payment_date})
                            else:
                                counterpart_aml_dict.update({'date': self.payment_date})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                            # raise ValidationError(_(counterpart_aml_dict))
                        else:
                            counterpart_aml_dict = self._get_shared_move_line_vals( debits,credits, amount_currencys, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                            counterpart_aml_dict.update({'currency_id': currency_ids})
                            counterpart_aml_dict.update({'account_id': id_account})
                            if self.payment_method_code == 'pdc':
                                counterpart_aml_dict.update({'date': self.payment_date})
                            else:
                                counterpart_aml_dict.update({'date': self.payment_date})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    else:
                        if self.payment_method_code == 'pdc':
                            if self.partner_type == 'customer':
                                liquidity_aml_dict = self._get_shared_move_line_vals(credits,debits,  -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': id_account})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                            # raise ValidationError(_(liquidity_aml_dict))
                            else:
                                liquidity_aml_dict = self._get_shared_move_line_vals( debits,credits, -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': id_account})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                                # raise ValidationError(_(liquidity_aml_dict))
                        else:
                            if self.partner_type == 'customer':
                                liquidity_aml_dict = self._get_shared_move_line_vals(credits, debits, -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': id_account})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                            else:
                                liquidity_aml_dict = self._get_shared_move_line_vals(debits,credits,  -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': id_account})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                                # raise ValidationError(_(liquidity_aml_dict))
                    
                    # self.add_variance_count = 1
            else:
                invoice_la = 'Variance Amount'
                id_account = self.var_account.id
                # aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
                # com = self.env['payment.variance.inv'].search([('payment_ids','=',rec.id)])
                # y = 0.0
                amt = 0.0
                # for x in com:
                #     y = y + x.var_amount
                #     amt = amt + x.invoice_amount
                amounts = self.var_amount
                for l in self.invoice_lines:
                    if l.allocation :
                        amt = amt + l.total_amount
                total_amt = amt
                
                if amounts != 0:
                    debits, credits, amount_currencys, currency_ids = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amounts, self.currency_id, self.company_id.currency_id)
                    
                    if amounts > 0:
                        #Write line corresponding to invoice payment
                        if self.partner_type == 'customer':
                            counterpart_aml_dict = self._get_shared_move_line_vals(credits,debits,  amount_currencys, move.id, False)
                            
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                            
                            counterpart_aml_dict.update({'currency_id': currency_ids})
                            if self.payment_method_code == 'pdc':
                                counterpart_aml_dict.update({'date': self.payment_date})
                            else:
                                counterpart_aml_dict.update({'date': self.payment_date})
                            # counterpart_aml_dict.update({'account_id': id_account})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                            # raise ValidationError(_('test'))
                            # raise ValidationError(_(counterpart_aml_dict))
                        else:
                            counterpart_aml_dict = self._get_shared_move_line_vals( debits,credits, amount_currencys, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                            counterpart_aml_dict.update({'currency_id': currency_ids})
                            # counterpart_aml_dict.update({'account_id': id_account})
                            if self.payment_method_code == 'pdc':
                                counterpart_aml_dict.update({'date': self.payment_date})
                            else:
                                counterpart_aml_dict.update({'date': self.payment_date})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                            # raise ValidationError(_(counterpart_aml_dict))
                    else:
                        if self.payment_method_code == 'pdc':
                            if self.partner_type == 'customer':
                                liquidity_aml_dict = self._get_shared_move_line_vals(credits,debits,  -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                                # raise ValidationError(_(liquidity_aml_dict))
                            else:
                                liquidity_aml_dict = self._get_shared_move_line_vals( debits,credits, -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                                # raise ValidationError(_(liquidity_aml_dict))
                        else:
                            if self.partner_type == 'customer':
                                liquidity_aml_dict = self._get_shared_move_line_vals(credits, debits, -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)
                                # raise ValidationError(_(liquidity_aml_dict))
                            else:
                                liquidity_aml_dict = self._get_shared_move_line_vals(debits,credits,  -amount_currencys, move.id, False)
                                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amounts))
                                if self.payment_method_code == 'pdc':
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                else:
                                    liquidity_aml_dict.update({'date': self.payment_date})
                                aml_obj.create(liquidity_aml_dict)

        # #######################################################################################################3
        # ########################################################################################################3
        #validate the payment
        # raise ValidationError(_('test'))
        # if not self.journal_id.post_at_bank_rec:
        move.post()
        

        if not len(self.invoice_ids) != 1:
            if not self.invoice_lines:
                # raise ValidationError(_('test'))
                if self.invoice_ids:
                    self.invoice_ids.register_payment(counterpart_aml)
        # 
        return move


    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment ")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note ")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note ")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment ")
            if invoice:
                name +=  invoice
                # for inv in invoice:
                #     if inv.move_id:
                #         name += inv.number + ', '
                # name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    # def _get_move_valsss(self, journal=None):
    #     """ Return dict to create the payment move
    #     """
    #     journal = journal or self.journal_id
    #     move_vals = {
    #         'date': self.payment_date,
    #         'ref': self.communication or '',
    #         'company_id': self.company_id.id,
    #         'journal_id': selfjournal_id.id,
    #     }
    #     if self.move_name:
    #         move_vals['name'] = self.move_name + 'release'
    #     return move_vals

    def _get_shared_move_line_valss(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'date':self.effective_date,
        }

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        move_vals = {
            'date': self.payment_date,
            'ref': str(self.communication) + '/' + str(self.cheque_reference) or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }
        if self.move_name:
            move_vals['name'] = self.move_name
        return move_vals

    @api.multi
    def _create_payment_entry_release(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
        Return the journal entry.
    """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.effective_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        # raise ValidationError(_("Test"))
        move_vals = {
            'date': self.effective_date,
            'ref': str(self.communication) + '/' + str(self.cheque_reference) + ' Release' or '',
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
        }
        if self.move_name:
            move_vals['name'] = self.move_name
        move = self.env['account.move'].create(move_vals)
        self.move_relase_id = move.id
        if self.var_amount < 0:
            amt = 0.0
            for l in self.invoice_lines:
                if l.allocation :
                    amt = amt + l.allocation
            amount = -amt
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.effective_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
            invoice_la = 'Receivables Relase Amount'
            invoice_pa = 'Payables Relase Amount'
            if self.partner_type == 'customer':
                counterpart_aml_dict = self._get_shared_move_line_valss(credit,debit,  amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml_dict.update({'account_id': self.journal_id.default_debit_account_id.id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
            else:
                counterpart_aml_dict = self._get_shared_move_line_valss(debit,credit, amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_pa))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml_dict.update({'account_id': self.journal_id.default_credit_account_id.id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
            
            #Reconcile with the invoices
            if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.effective_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
                writeoff_line['name'] = self.writeoff_label
                writeoff_line['account_id'] = self.writeoff_account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line = aml_obj.create(writeoff_line)
                if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo

            #Write counterpart lines
            if not self.currency_id.is_zero(self.amount):
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        aml_obj.create(liquidity_aml_dict)
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        aml_obj.create(liquidity_aml_dict)
                else:
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        aml_obj.create(liquidity_aml_dict)
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss(credit, debit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        aml_obj.create(liquidity_aml_dict)
        else:
            invoice_la = 'Receivables Relase Amount'
            invoice_pa = 'Payables Relase Amount'
            #Write line corresponding to invoice payment
            if self.partner_type == 'customer':
                counterpart_aml_dict = self._get_shared_move_line_valss(credit,debit,  amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_la))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml_dict.update({'account_id': self.journal_id.default_debit_account_id.id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
            else:
                counterpart_aml_dict = self._get_shared_move_line_valss(credit,debit, amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_pa))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml_dict.update({'account_id': self.journal_id.default_credit_account_id.id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
            
            #Reconcile with the invoices
            if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
                writeoff_line['name'] = self.writeoff_label
                writeoff_line['account_id'] = self.writeoff_account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line = aml_obj.create(writeoff_line)
                if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo

            #Write counterpart lines
            if not self.currency_id.is_zero(self.amount):
                if self.payment_method_code == 'pdc':
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        aml_obj.create(liquidity_aml_dict)
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        liquidity_aml_dict.update({'account_id': self.pdc_account.id})
                        aml_obj.create(liquidity_aml_dict)
                else:
                    if self.partner_type == 'customer':
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss( debit,credit, -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        aml_obj.create(liquidity_aml_dict)
                    else:
                        if not self.currency_id != self.company_id.currency_id:
                            amount_currency = 0
                        liquidity_aml_dict = self._get_shared_move_line_valss(debit,credit,  -amount_currency, move.id, False)
                        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                        aml_obj.create(liquidity_aml_dict)

        #validate the payment
        # if not self.journal_id.post_at_bank_rec:
        #     move.action_release()

        #reconcile the invoice receivable/payable line(s) with the payment
        # if self.invoice_ids:
        #     self.invoice_ids.register_payment(counterpart_aml)
        self.release_count = 1
        self.release_check = True
        return move


    @api.multi
    def action_release(self):
        for rec in self:

            # if any(inv.state != 'open' for inv in rec.invoice_ids):
            #     raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry_release(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            # rec.write({'state': 'posted', 'move_name': move.name})
        return True


    @api.multi
    def button_journal_entries_release(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('move_id', '=', self.move_relase_id)],
        }

    @api.multi
    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            # for l in counter_array:
            #     cov  = self.env['account.move.line'].search([('id','=',l['id'])])
            #     cos  = self.env['account.move.line'].search([('id','=',l['m_id'])])
            #     cov.remove_move_reconcile()
            #     cos.remove_move_reconcile()

            if self.release_count != 0 :
                com = self.env['account.move'].search([('id','=',self.move_relase_id)])
                for mov in com:
                    if rec.invoice_ids:
                        mov.line_ids.remove_move_reconcile()
                    mov.button_cancel()
                    mov.unlink()
                self.release_count = 0
                self.release_check = False
            rec.add_variance_count = 0
            rec.state = 'cancelled'
            outstan = self.env['payment.invoice.line.outstand'].search([('amount','=',0)])
            for stan in outstan:
                if stan.amount == 0 :
                    stan.unlink()

    @api.multi
    def add_variance(self):
        for rec in self:
            if rec.var_account:
                id_account = rec.var_account.id
                amt = 0.0
                amounts = rec.var_amount
                for l in rec.invoice_lines:
                    if l.allocation :
                        amt = amt + l.total_amount
                total_amt = amt

                if amounts != 0:
                    debits, credits, amount_currencys, currency_ids = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amounts, self.currency_id, self.company_id.currency_id)

                    #Write line corresponding to invoice payment
                    if self.partner_type == 'customer':
                        counterpart_aml_dict = self._get_shared_move_line_valss(credist,debits,  amount_currencys, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'account_id': id_account})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    else:
                        counterpart_aml_dict = self._get_shared_move_line_valss(debits,credits, amount_currencys, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml_dict.update({'account_id': id_account})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                
                    rec.add_variance_count = 1
            else:
                raise ValidationError(_("Please add the variance account"))

    
    
    @api.multi
    def get_outstanding_info(self):
        # self.outstanding_credits_debits_widget = json.dumps(False)
        
        com = self.env['payment.invoice.line.outstand']
        # if self.state == 'open':
        if self.invoice_lines:
            for l in self.invoice_lines:
                accountname = l.account_id.id
        else:
            if self.partner_type == 'customer':
                accountname = self.partner_id.property_account_receivable_id.id
            else:
                accountname = self.partner_id.property_account_payable_id.id
        domain = [('account_id', '=', accountname),('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),('reconciled', '=', False),'|','&', ('amount_residual_currency', '!=', 0.0), ('currency_id','!=', None),'&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id','=', None), ('amount_residual', '!=', 0.0)]
        # if self.type in ('out_invoice', 'in_refund'):
        #     domain.extend([('credit', '>', 0), ('debit', '=', 0)])
        #     type_payment = _('Outstanding credits')
        # else:
        #     domain.extend([('credit', '=', 0), ('debit', '>', 0)])
        #     type_payment = _('Outstanding debits')
        info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
        
        lines = self.env['account.move.line'].search(domain)
        
        currency_id = self.currency_id
        
        if len(lines) != 0:
            for line in lines:
                # raise ValidationError(_(line))
                # get the outstanding residual value in invoice currency
                if line.currency_id and line.currency_id == self.currency_id:
                    amount_to_show = abs(line.amount_residual_currency)
                else:
                    currency = line.company_id.currency_id
                    amount_to_show = currency._convert(abs(line.amount_residual), self.currency_id, self.company_id, line.date or fields.Date.today())
                if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                    continue
                if line.ref :
                    title = '%s' % (line.move_id.name)
                else:
                    title = line.move_id.name
                # info['content'].append({
                #     'journal_name': line.ref or line.move_id.name,
                #     'title': title,
                #     'amount': amount_to_show,
                #     'currency': currency_id.symbol,
                #     'id': line.id,
                #     'position': currency_id.position,
                #     'digits': [69, self.currency_id.decimal_places],
                # })
                # if line.payment_id:
                cov = com.search([('payment_id','=',self.id),('move_id','=',line.id)])
                if cov:
                    cov.write({'open_amount':amount_to_show,'allocation':amount_to_show})

                else:
                    if line.partner_id.id == self.partner_id.id:
                        if self.partner_type == 'customer':

                            if line.credit:
                                vals = {
                                    'payment_id':self.id,
                                    'title':title,
                                    'open_amount':amount_to_show,
                                    'allocation':amount_to_show,
                                    'move_id':line.id,
                                }
                        
                                cos = com.create(vals)
                        else:
                            if line.debit:
                                vals = {
                                    'payment_id':self.id,
                                    'title':title,
                                    'open_amount':amount_to_show,
                                    'allocation':amount_to_show,
                                    'move_id':line.id,
                                }
                        
                                cos = com.create(vals)
            
            self.add_variance_count = 1

    @api.multi
    def update_invoice_lines(self):
        for inv in self.invoice_lines:
            inv.open_amount = inv.invoice_id.residual 
        self.onchange_partner_id()
        self.get_outstanding_info()
                # raise ValidationError(_(cos.id))
                # info['title'] = type_payment
                # self.outstanding_credits_debits_widget = json.dumps(info)
                # self.has_outstanding = True

# class PaymentInvoiceLineCus(models.Model):
#     _inherit = 'payment.invoice.line'

#     move_id_outstand = fields.Many2one('account.move.line', string="Move Line")
#     outstand = fields.Boolean('Outstand allocation',default=False)


class PaymentInvoiceLineOutstand(models.Model):
    _name = 'payment.invoice.line.outstand'
    
    payment_id = fields.Many2one('account.payment', string="Payment")
    # invoice_id = fields.Many2one('account.invoice', string="Invoice")
    move_id = fields.Many2one('account.move.line', string="Move Line")
    title = fields.Char('Title')
    # account_id = fields.Many2one(related="invoice_id.account_id", string="Account")
    # currency = fields.Char('Currency')
    due_date = fields.Char('Due Date', compute='_get_invoice_data')
    amount = fields.Float('Total Amount', compute='_get_invoice_data')
    open_amount = fields.Float(string='Due Amount')
    allocation = fields.Float(string='Allocation ')
    
    # @api.multi
    # @api.onchange('open_amount')
    # def _get_invoice_data(self):
    #     for data in self:
    #         data.allocation = data.open_amount


    @api.multi
    @api.depends('move_id')
    def _get_invoice_data(self):
        for data in self:
            move_id = data.move_id
            data.due_date = move_id.date_maturity
            # data.open_amount = move_id.amount_residual
            # data.title = move_id.ref
            if move_id.debit :
                data.amount = move_id.debit 
            else:
                data.amount = move_id.credit
            # data.allocation = data.open_amount



    # @api.multi
    # def action_add(self):
    #     for rec in self:
    #         if rec.invoice_id:
    #             # cos = self.env['account.invoice'].search([('id','=',rec.invoice_id.id)])
    #             com = self.env['payment.invoice.line']
    #             vals={
    #                 'payment_id':rec.payment_id.id,
    #                 'invoice_id':rec.invoice_id.id,
    #                 'allocation':rec.amount,
    #                 'outstand':True,
    #                 'move_id_outstand': rec.move_id.id
    #             }
    #             com.create(vals)
    #             # mid = rec.move_id.id
    #             # cos.assign_outstanding_credit(mid)
    #             rec.unlink()
                
    #         else:
    #             raise ValidationError(_("Please add the invoice Number"))

class AccountJournalcus(models.Model):
    _inherit = 'account.journal'

    @api.multi
    def name_get(self):
        res = []
        for journal in self:
            # currency = journal.currency_id or journal.company_id.currency_id
            name = "%s" % (journal.name)
            res += [(journal.id, name)]
        return res


# class BankDetails(models.Model):
#     _name = 'bank.details'
#     _inherit = 'mail.thread'

#     name = fields.Many2one('account.journal',string='Bank Name',required=True,track_visibility="onchange")
#     bank_name = fields.Char(string='Bank Name',required=True,track_visibility="onchange")
#     branch = fields.Char('Branch',required=True,track_visibility="onchange")
#     currency = fields.Many2one('res.currency',string='Currency Type')
#     acc_no = fields.Char(string='Account No',required=True)
#     ban = fields.Many2one('res.bank',related='name.bank_id',store=True,string='Account No')
#     swift_code = fields.Char('Swift Code',required=True,track_visibility="onchange")
#     iban = fields.Char('IBAN',required=True,track_visibility="onchange")

#     @api.onchange('name')
#     def _get_accdata(self):
#         for rec in self:
#             rec.acc_no = rec.name.bank_acc_number
#             rec.currency = rec.name.currency_id.id

#     @api.onchange('ban')
#     def _get_swift(self):
#         for rec in self:
#             if rec.ban:
#                 rec.swift_code = rec.ban.bic
#             else:
#                 continue

class AccountMoveCustomize(models.Model):
    _inherit = 'account.move'

#     prepare = fields.Char('Prepared by')
#     checked = fields.Char('Checked by')
#     received = fields.Char('Received by')
#     approved = fields.Char('Approved by')
#     verified = fields.Char('Verified by')
#     check_amount = fields.Float('Amount')
#     partner = fields.Char(string="Partner Name")
#     AC_print = fields.Boolean('Print A/c Payee')
#     check_amount_in_words = fields.Char('amount in word',compute="_onchange_amount")
#     document_count = fields.Integer(compute='_document_count', string='# Documents')
    

#     @api.multi
#     def _document_count(self):
#         for each in self:
#             document_ids = self.env['account.move.document'].sudo().search([('pay_ref', '=', each.id)])
#             each.document_count = len(document_ids)

#     @api.multi
#     def document_view(self):
#         self.ensure_one()
#         domain = [('pay_ref', '=', self.id)]
#         return {
#             'name': _('Documents'),
#             'domain': domain,
#             'res_model': 'account.move.document',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'tree,form',
#             'view_type': 'form',
#             'help': _('''<p class="oe_view_nocontent_create">
#                            Click to Create New Documents
#                         </p>'''),
#             'limit': 80,
#             'context': "{'default_pay_ref': '%s'}" % self.id
#         }


#     @api.depends('check_amount','currency_id')
#     @api.onchange('check_amount','currency_id')
#     def _onchange_amount(self):
#         # res = super(AccountMoveCustomize, self)._onchange_amount()
#         self.check_amount_in_words = self.currency_id.amount_to_text(self.check_amount) if self.currency_id else ''
#         self.check_amount_in_words = self.check_amount_in_words.replace(' Dirham ', ' ').replace(' Dirham',' ').replace(' And ',' ')

#         # return res

    @api.constrains('line_ids', 'journal_id', 'auto_reverse', 'reverse_date')
    def _validate_move_modification(self):
        if 'posted' in self.mapped('line_ids.payment_id.state'):
            y = 1

#     @api.model
#     def create(self, vals):
#         vals['prepare'] = self.env.user.name
#         move = super(AccountMoveCustomize, self.with_context(check_move_validity=False, partner_id=vals.get('partner_id'))).create(vals)
#         move.assert_balanced()
#         return move

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'posted':
            vals['approved'] = self.env.user.name
        if 'line_ids' in vals:
            res = super(AccountMoveCustomize, self.with_context(check_move_validity=False)).write(vals)
            self.assert_balanced()
        else:
            res = super(AccountMoveCustomize, self).write(vals)
        return res
            # raise ValidationError(_("You cannot modify a journal entry linked to a posted payment."))



class AccountMoveLineCus(models.Model):
    _inherit = 'account.move.line'
    
    def _check_reconcile_validity(self):
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        # if len(set(all_accounts)) > 1:
        #     raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (all_accounts[0].name, all_accounts[0].code))

# Accounts Customization Part















