# Copyright 2019-2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoiced = fields.Boolean(
        string="Invoiced", compute="_compute_invoiced", store=True
    )
    partner_ref = fields.Char(
        string="Vendor Bill Reference", store=True, compute="_compute_partner_ref"
    )
    image_medium = fields.Binary(related="product_id.image_medium", string="image")
    sale_order_partner_id = fields.Many2one(
        related="order_id.group_id.sale_id.partner_id", string="Sales Order Customer"
    )
    sale_order_line_price_unit = fields.Float(
        compute="_compute_sale_order_line_price_unit", string="Sales Order Price"
    )
    sale_order_currency_id = fields.Many2one(
        related="order_id.group_id.sale_id.currency_id"
    )
    propose_margin = fields.Float(
        string="Propose Margin (HKD)", compute="_compute_propose_margin"
    )

    @api.multi
    @api.depends(
        "order_id.partner_ref",
        "invoice_lines.invoice_id.reference",
        "invoice_lines.invoice_id.state",
    )
    def _compute_partner_ref(self):
        for line in self:
            if line.invoice_lines.filtered(lambda a: a.invoice_id.state != "cancel"):
                line.partner_ref = line.invoice_lines.filtered(
                    lambda a: a.invoice_id.state != "cancel"
                )[0].invoice_id.reference
            else:
                line.partner_ref = line.order_id.partner_ref

    @api.multi
    @api.depends("qty_invoiced", "product_qty")
    def _compute_invoiced(self):
        for line in self:
            line.invoiced = False if line.qty_invoiced < line.product_qty else True

    @api.multi
    def _compute_sale_order_line_price_unit(self):
        for line in self:
            if line.order_id.group_id and line.order_id.group_id.sale_id:
                sale_order_line = line.order_id.group_id.sale_id.order_line.filtered(
                    lambda l: l.lot_id == line.lot_id
                )
                if sale_order_line:
                    line.sale_order_line_price_unit = sale_order_line.price_unit

    @api.multi
    def makeInvoices(self):
        context = self.env.context or {}
        record_ids = context.get("active_ids", [])

        if record_ids:
            res = False
            invoices = {}
            purchase_line_obj = self.env["purchase.order.line"]
            invoice_line_obj = self.env["account.invoice.line"]

            for line in purchase_line_obj.browse(record_ids):
                if not line.invoiced and (line.state not in ("draft", "cancel")):
                    if line.partner_id.id not in invoices:
                        invoices[line.partner_id.id] = []
                    invoice_line_vals = line._prepare_invoice_line_vals()
                    invoice_line_vals.update({"origin": line.order_id.name})
                    invoice_line = invoice_line_obj.create(invoice_line_vals)
                    line.write(
                        {
                            "qty_invoiced": line.qty_invoiced
                            or 0 + invoice_line.quantity,
                            "invoice_lines": [(4, invoice_line.id)],
                        }
                    )
                    invoices[line.partner_id.id].append((line, invoice_line))
            res = []
            for result in invoices.values():
                invoice_line_ids = list(map(lambda x: x[1].id, result))
                orders = list(set(map(lambda x: x[0].order_id, result)))
                res.append(
                    self._make_invoice_by_partner(
                        orders[0].partner_id, orders, invoice_line_ids
                    )
                )
        return {
            "name": _("Supplier Invoices"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.invoice",
            "domain": "[('id','in', [" + ",".join(map(str, res)) + "])]",
            "view_id": False,
            "context": "{'type':'in_invoice', 'journal_type': 'purchase'}",
            "type": "ir.actions.act_window",
        }

    @api.multi
    def _prepare_invoice_line_vals(self):
        self.ensure_one()
        account_id = (
            self.product_id.product_tmpl_id._get_product_accounts()["stock_output"]
            if self.order_id.is_vci
            else self.product_id.product_tmpl_id._get_product_accounts()["stock_input"]
        )
        return {
            "name": self.name,
            "account_id": account_id.id,
            "price_unit": self.price_unit or 0.0,
            "quantity": self.product_qty,
            "product_id": self.product_id.id or False,
            "quant_id": self.quant_id.id or False,
            "invoice_line_tax_ids": [(6, 0, [x.id for x in self.taxes_id])],
            "purchase_line_id": self.id,
        }

    def _make_invoice_by_partner(self, partner, orders, lines_ids):
        """
            create a new invoice for one supplier
            @param partner : The object partner
            @param orders : The set of orders to add in the invoice
            @param lines : The list of line's id
        """
        account_journal_obj = self.env["account.journal"]
        invoice_obj = self.env["account.invoice"]
        name = orders and ",".join([order.name for order in orders if order.name]) or ""
        reference = (
            orders
            and ",".join([order.partner_ref for order in orders if order.partner_ref])
            or ""
        )
        journal_id = account_journal_obj.search([("type", "=", "purchase")])
        journal_id = journal_id and journal_id[0].id or False
        account_id = partner.property_account_payable_id.id
        invoice_vals = {
            "name": name,
            "origin": name,
            "type": "in_invoice",
            "journal_id": journal_id,
            "reference": reference,
            "account_id": account_id,
            "partner_id": partner.id,
            "invoice_line_ids": [(6, 0, lines_ids)],
            "currency_id": orders
            and orders[0].currency_id.id
            or self.env.user.company_id.currency_id,
            "comment": orders
            and " \n".join([order.notes for order in orders if order.notes])
            or "",
            "payment_term_id": orders and orders[0].payment_term_id.id or False,
            "fiscal_position_id": partner.property_account_position_id.id,
        }
        invoice_id = invoice_obj.create(invoice_vals).id
        for order in orders:
            order.write({"invoice_ids": [(4, invoice_id)]})
        return invoice_id

    @api.multi
    def _compute_propose_margin(self):
        for line in self:
            sale_base_price = (
                line.sale_order_currency_id.compute(
                    line.sale_order_line_price_unit,
                    self.env.user.company_id.currency_id,
                )
                if line.sale_order_currency_id != self.env.user.company_id.currency_id
                else line.sale_order_line_price_unit
            )
            purchase_base_price = (
                line.currency_id.compute(
                    line.price_unit, self.env.user.company_id.currency_id
                )
                if line.currency_id != self.env.user.company_id.currency_id
                else line.price_unit
            )
            line.propose_margin = sale_base_price - purchase_base_price
