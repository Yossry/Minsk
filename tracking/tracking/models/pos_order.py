# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
import datetime

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_taxes_lx(self, price):
        """ Used in on_change to set taxes and price"""
        self.ensure_one()
        if self.invoice_id.type not in ('out_invoice', 'out_refund'):
            self.ensure_one()
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids or self.invoice_id.company_id.account_sale_tax_id
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids or self.invoice_id.company_id.account_purchase_tax_id

            # Keep only taxes of the company
            company_id = self.company_id or self.env.user.company_id
            taxes = taxes.filtered(lambda r: r.company_id == company_id)

            self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)

            fix_price = self.env['account.tax']._fix_tax_included_price
            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                prec = self.env['decimal.precision'].precision_get('Product Price')
                if not self.price_unit or float_compare(price, self.product_id.standard_price, precision_digits=prec) == 0:
                    self.price_unit = fix_price(price, taxes, fp_taxes)
                    self._set_currency()
            else:
                self.price_unit = fix_price(price)
                self._set_currency()
        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            self.ensure_one()
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids or self.invoice_id.company_id.account_sale_tax_id
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids or self.invoice_id.company_id.account_purchase_tax_id

            # Keep only taxes of the company
            company_id = self.company_id or self.env.user.company_id
            taxes = taxes.filtered(lambda r: r.company_id == company_id)
            mytaxes = self.env['account.tax']

            lista = []
            for x in taxes:
                if self.partner_id.show_ieps == False:
                    ieps = False
                    for z in x.tag_ids:
                        if z.name == 'IEPS':
                            ieps = True
                    if ieps == False:
                        lista.append(x.id)
                else:
                    lista.append(x.id)

            amount_ieps = 0
            for x in taxes:
                ieps = False
                for z in x.tag_ids:
                    if z.name == 'IEPS':
                        ieps = True
                if ieps == True:
                    amount_ieps += x.amount
            print("Factura-Impuestos ",taxes, lista)
            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)
            else:
                self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(mytaxes.search([('id','in',lista)]), self.product_id, self.invoice_id.partner_id)

            fix_price = self.env['account.tax']._fix_tax_included_price
            fixx_price = mytaxes.search([('id','in',lista)])._fix_tax_included_price
            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                prec = self.env['decimal.precision'].precision_get('Product Price')
                if not self.price_unit or float_compare(price, self.product_id.standard_price, precision_digits=prec) == 0:
                    self.price_unit = fix_price(price, taxes, fp_taxes)
                    self._set_currency()
            else:
                self.price_unit = fixx_price(price, mytaxes.search([('id','in',lista)]), fp_taxes)
                self._set_currency()

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def compute_onchange_invoice_line_ids(self):
    #     self.fun_invoice_line_ids()
    #     print("fun_invoice_line_ids")
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        # taxes_grouped = self.get_taxes_values()
        # tax_lines = self.tax_line_ids.filtered('manual')
        # for tax in taxes_grouped.values():
        #     tax_lines += tax_lines.new(tax)
        # self.tax_line_ids = tax_lines
        # taxes_groupedi = self.get_taxes_values_ieps()
        # tax_linesi = self.line_tax_ids_ieps.filtered('manual')
        # for tax in taxes_groupedi.values():
        #     tax_linesi += tax_linesi.new(tax)
        # self.line_tax_ids_ieps = tax_linesi
        return

class PosOrder(models.Model):
    _inherit = 'pos.order'
    monto_credito = fields.Float(string="Credito Solicitado")
    abono_credito = fields.Float(string="Abono al credito")
    orden_ruta_id = fields.Many2one('route.order', string="Ruta Origen")
    folio_venta = fields.Char(string="Folio de venta", help="Folio comunmente proporcionado por tiendas OXXO")
    direccion_cliente_id = fields.Many2one('res.partner',string="Direccion de envio")

    @api.multi
    def action_pos_order_invoicepayment_create(self):
        self.recalcula_descuento()
        self.action_pos_order_invoice_create()
        # self.create_payment_pos_invoice_lx(self.invoice_id.id)
        return True

    @api.multi
    def recalcula_descuento(self):
        for order in self:
            td = 0
            tl = 0
            for x in order.lines:
                if x.price_subtotal_incl <=0:
                    td += x.price_subtotal_incl
                else:
                    tl += x.price_subtotal_incl

            percent = ((td*-1)/tl)*100

            for x in order.lines:
                if x.price_subtotal_incl <=0:
                    x.unlink()
                else:
                    x.discount += percent




    @api.multi
    def action_pos_order_invoice_create(self):
        Invoice = self.env['account.invoice']

        for order in self:
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            invoice = Invoice.new(order._prepare_invoice())
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                if line.price_subtotal_incl > 0:
                    self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

            new_invoice.with_context(local_context).sudo().compute_taxes()
            new_invoice.compute_onchange_invoice_line_ids()
            order.sudo().write({'state': 'invoiced'})
            # try:
            #     Invoice.action_invoice_open()
            # except:
            #     print("ERROR AL VALIDAR FACTURA")
            # if not Invoice.l10n_mx_edi_cfdi_uuid:
            #     try:
            #         Invoice.l10n_mx_edi_update_pac_status()
            #     except:
            #         print("ERROR AL TIMBRAR FACTURA")
            if self.direccion_cliente_id:
                Invoice.partner_shipping_id = self.direccion_cliente_id.id
            if Invoice.move_id:
                self.account_move = Invoice.move_id
        return Invoice.id

    @api.multi
    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    @api.multi
    def action_pos_order_invoice_create_credito(self):
        if self.state != 'invoiced':
            monto = float(self.monto_credito)
            invoice_obj = self.env["account.invoice"]
            invoice_line_obj = self.env["account.invoice.line"]
            prd_account_id = self._default_account()
            for rec in self:
                # Create Invoice
                if rec.partner_id:
                    curr_invoice = {
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.partner_id.property_account_receivable_id.id,
                        'state': 'draft',
                        'type':'out_invoice',
                        'date_invoice':datetime.date.today(),
                        'origin': "PosOrder: " + rec.name,
                        'sequence_number_next_prefix': False
                    }

                    inv_ids = invoice_obj.create(curr_invoice)
                    inv_id = inv_ids.id

                    if inv_ids:
                        # Create Invoice line
                        curr_invoice_line = {
                            'name': "Credito por venta "+str(rec.name),
                            'price_unit': monto or 0,
                            'quantity': 1,
                            'account_id': prd_account_id,
                            'invoice_id': inv_id,
                        }
                        print("CREAR FACTURA ::::::",curr_invoice_line)

                        inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                        inv_line_ids._set_taxes_lx(monto)
                        print(inv_line_ids.product_id.name,inv_line_ids.price_unit)
                    inv_ids._onchange_invoice_line_ids()
                    inv_ids._onchange_invoice_line_ids_ieps()
                    # inv_ids.invoice_line_move_line_get()
                    inv_ids.get_taxes_values()
                    # try:
                    #     inv_ids.action_invoice_open()
                    # except:
                    #     print("ERROR AL VALIDAR FACTURA")
                    # if not inv_ids.l10n_mx_edi_cfdi_uuid:
                    #     try:
                    #         inv_ids.l10n_mx_edi_update_pac_status()
                    #     except:
                    #         print("ERROR AL TIMBRAR FACTURA")
                    # try:
                    #     rec.create_payment_pos_invoice_lx(inv_ids.id)
                    # except:
                    #     print("NO PUDO CREARSE EL PAGO")
            return True
        else:
            return True

    # @api.multi
    # def action_pos_order_invoice_create(self):
    #     invoice_obj = self.env["account.invoice"]
    #     invoice_line_obj = self.env["account.invoice.line"]

    #     for rec in self:
    #         # Create Invoice
    #         if rec.partner_id:
    #             curr_invoice = {
    #                 'partner_id': rec.partner_id.id,
    #                 'account_id': rec.partner_id.property_account_receivable_id.id,
    #                 'state': 'draft',
    #                 'type':'out_invoice',
    #                 'date_invoice':datetime.date.today(),
    #                 'origin': "PosOrder: " + rec.name,
    #                 'sequence_number_next_prefix': False
    #             }

    #             inv_ids = invoice_obj.create(curr_invoice)
    #             inv_id = inv_ids.id

    #             if inv_ids:
    #                 for x in rec.lines:

    #                     # Create Invoice line
    #                     curr_invoice_line = {
    #                         'name': x.product_id.name,
    #                         'product_id': x.product_id.id,
    #                         'price_unit': x.price_unit or 0,
    #                         'quantity': x.qty,
    #                         'account_id': x.product_id.categ_id.property_account_income_categ_id.id,
    #                         'invoice_id': inv_id,
    #                         'uom_id': x.product_id.uom_id.id,
    #                         'invoice_line_tax_ids': [(6,0,x.product_id.taxes_id.ids)]
    #                     }
    #                     print("CREAR FACTURA ::::::",curr_invoice_line)

    #                     inv_line_ids = invoice_line_obj.create(curr_invoice_line)
    #                     inv_line_ids._set_taxes_lx(x.price_unit)
    #                     print(inv_line_ids.product_id.name,inv_line_ids.price_unit)
    #             inv_ids.compute_onchange_invoice_line_ids()
    #             for x in inv_ids.invoice_line_ids:
    #                 print("1",x.product_id.name,x.price_unit)
    #             inv_ids.invoice_line_move_line_get()
    #             for x in inv_ids.invoice_line_ids:
    #                 print("2",x.product_id.name,x.price_unit)
    #             inv_ids.get_taxes_values()
    #             for x in inv_ids.invoice_line_ids:
    #                 print("3",x.product_id.name,x.price_unit)
    #             try:
    #                 inv_ids.action_invoice_open()
    #             except:
    #                 print("ERROR AL VALIDAR FACTURA")
    #             if not inv_ids.l10n_mx_edi_cfdi_uuid:
    #                 try:
    #                     inv_ids.l10n_mx_edi_update_pac_status()
    #                 except:
    #                     print("ERROR AL TIMBRAR FACTURA")
    #             rec.invoice_id = inv_ids.id
    #             # try:
    #             #     rec.create_payment_pos_invoice_lx(inv_ids.id)
    #             # except:
    #             #     print("NO PUDO CREARSE EL PAGO")
    #     return True

    @api.multi
    def create_payment_pos_invoice_lx_abono(self):
        self.ensure_one()
        abono = self.abono_credito
        payment_type = 'inbound'
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        vals = {
            'amount' : abono,
            'journal_id' : 12,
            'payment_date' : datetime.datetime.now(),
            'communication': '',
            'partner_id': self.partner_id.id,
            'partner_type': 'customer',
            'payment_type': payment_type,
            'payment_method_id': payment_method.id
         }
        payment = self.env['account.payment'].create(vals)
        try:
            payment.post()
        except:
            print("ERROR AL CONFIRMAR PAGO")
            return True
        return True

    @api.multi
    def create_payment_pos_invoice_lx(self, invid):
        self.ensure_one()
        inv = self.env["account.invoice"].search([('id','=',invid)])
        payment_type = inv.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
        if payment_type == 'inbound':
            payment_method = self.env.ref('account.account_payment_method_manual_in')
        else:
            payment_method = self.env.ref('account.account_payment_method_manual_out')
        vals = {
            'invoice_ids': [(6, 0, inv.ids)],
            'amount' : self.amount_paid,
            'journal_id' : 12,
            'payment_date' : datetime.datetime.now(),
            'communication': inv.number,
            'partner_id': inv.partner_id.id,
            'partner_type': inv.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
            'payment_type': payment_type,
            'payment_method_id': payment_method.id
         }
        print(vals)
        payment = self.env['account.payment'].create(vals)
        try:
            payment.post()
        except:
            try:
                payment.post()
            except:
                print("ERROR AL CONFIRMAR PAGO")
                try:
                    payment.l10n_mx_edi_update_pac_status()
                except:
                    print("ERROR AL CONFIRMAR PAGO EN 2DO INTENTO. FORZANDO REP")
                    try:
                        payment.l10n_mx_edi_force_payment_complement()
                    except:
                        print("ERROR EN TODOS LOS INTENTOS")
                        return True
        return True