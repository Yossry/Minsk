# -*- coding: utf-8 -*-
""" init object """
from functools import partial
from odoo import fields, models, api, _
from odoo.tools import formatLang


import logging

LOGGER = logging.getLogger(__name__)

class AccountInvoiceGroup(models.Model):
    _name = 'account.invoice.group'
    _rec_name = 'name'
    _description = 'Account Invoice Group'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", domain=[('customer','=',True)] )
    # invoice_type = fields.Selection(string="Status",default="inv", selection=[('inv', 'Customer Invoices Only'), ('inv_refund', 'Invoices And Refunds'), ], required=False, )
    description = fields.Text()
    invoice_type = fields.Selection(default="out_invoice", selection=[('out_invoice', 'Customer Invoice'), ('out_refund', 'Customer Credit Note'), ], required=False, )
    invoice_ids = fields.One2many(comodel_name="account.invoice", inverse_name="account_invoice_group_id",)
    sale_order_ids = fields.Many2many(comodel_name="sale.order", compute='compute_invoice_line_ids',)
    invoice_line_ids = fields.Many2many(comodel_name="account.invoice.line",compute='compute_invoice_line_ids')
    state = fields.Selection(string="Status",default="draft", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ], required=False, )
    inv_count = fields.Integer(compute='compute_invoice_line_ids')
    sale_order_count = fields.Integer(compute='compute_invoice_line_ids')
    code = fields.Char()

    @api.model
    def create(self,vals):
        if 'invoice_type' in vals and vals.get('invoice_type') == 'out_invoice' or self._context.get('default_invoice_type') == 'out_invoice':
            vals['code'] = self.env['ir.sequence'].next_by_code('group.customer.invoice')
        if 'invoice_type' in vals and vals.get('invoice_type') == 'out_refund' or self._context.get('default_invoice_type') == 'out_refund':
            vals['code'] = self.env['ir.sequence'].next_by_code('group.customer.credit.note')
        return super(AccountInvoiceGroup,self).create(vals)

    @api.multi
    def action_open_invoices(self):
        search_view_ref = self.env.ref('account.view_account_invoice_filter', False)
        form_view_ref = self.env.ref('account.invoice_form', False)
        tree_view_ref = self.env.ref('account.invoice_tree', False)
        for one in self:
            domain = [('id', 'in', one.invoice_ids.ids)]
            view_tree = {
                'name': _(' Invoices '),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': domain,
                'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
                'search_view_id': search_view_ref and search_view_ref.id,
                'context': {'default_partner_id': one.partner_id.id,'default_account_invoice_group_id': one.id,'default_type':'out_invoice', 'type':'out_invoice', 'journal_type': 'sale'},

            }
            return view_tree

    @api.multi
    def action_open_order(self):
        for one in self:
            domain = [('id', 'in', one.sale_order_ids.ids)]
            view_tree = {
                'name': _(' Sale Orders '),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'domain': domain,
            }
            return view_tree

    def compute_invoice_line_ids(self):
        for rec in self:
            rec.inv_count = len(rec.invoice_ids)
            inv_lines = rec.invoice_ids.mapped('invoice_line_ids')
            rec.invoice_line_ids = inv_lines.ids
            sale_order_lines = inv_lines.mapped('sale_line_ids')
            sale_orders = sale_order_lines.mapped('order_id')
            rec.sale_order_ids = sale_orders.ids
            rec.sale_order_count = len(sale_orders)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals and vals.get('partner_id') != self.partner_id.id:
            self.invoice_ids.write({'account_invoice_group_id': None})
        return super(AccountInvoiceGroup,self).write(vals)

    def _amount_by_group(self):
        currency = self.invoice_ids.mapped('currency_id')[-1]
        fmt = partial(formatLang, self.with_context(lang=self.partner_id.lang).env, currency_obj=currency)
        res = {}
        for line in self.invoice_ids.mapped('tax_line_ids'):
            res.setdefault(line.tax_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
            res[line.tax_id.tax_group_id]['amount'] += line.amount_total
            res[line.tax_id.tax_group_id]['base'] += line.base
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        return [(
            r[0].name, r[1]['amount'], r[1]['base'],
            fmt(r[1]['amount']), fmt(r[1]['base']),
            len(res),
        ) for r in res]





