# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.multi
    def _run_buy(
        self, product_id, product_qty, product_uom, location_id, name, origin, values
    ):
        cache = {}
        if "move_dest_ids" in values:
            for move in values["move_dest_ids"]:
                if not move.quant_id.owner_id:
                    raise UserError(
                        _(
                            "Owner is missing from from the %s (%s)."
                            % (move.product_id.display_name, move.quant_id.display_name)
                        )
                    )
                values.update(
                    {
                        "quant_id": move.quant_id.id,
                        "price_unit": move.quant_id.purchase_price_unit,
                        "currency_id": move.quant_id.currency_id.id,
                    }
                )
                order_line = move.sale_line_id
                partner = move.quant_id.owner_id
        # <<< QTL Edit
        # We use the owner of the stock as the supplier
        # suppliers = product_id.seller_ids\
        #     .filtered(lambda r: (not r.company_id or r.company_id == values['company_id']) and (not r.product_id or r.product_id == product_id) and r.name.active) # noqa
        # if not suppliers:
        #     msg = _('There is no vendor associated to the product %s. Please define a vendor for this product.') % ( # noqa
        #         product_id.display_name,)
        #     raise UserError(msg)
        # supplier = self._make_po_select_supplier(values, suppliers)
        # partner = supplier.name
        # we put `supplier_info` in values for extensibility purposes
        # values['supplier'] = supplier
        # >>> QTL Edit
        domain = self._make_po_get_domain(values, partner)
        if domain in cache:
            po = cache[domain]
        else:
            po = self.env["purchase.order"].sudo().search([dom for dom in domain])
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order(
                product_id, product_qty, product_uom, origin, values, partner
            )
            company_id = (
                values.get("company_id")
                and values["company_id"].id
                or self.env.user.company_id.id
            )
            po = (
                self.env["purchase.order"]
                .with_context(force_company=company_id)
                .sudo()
                .create(vals)
            )
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(", "):
            if po.origin:
                if origin:
                    po.write({"origin": po.origin + ", " + origin})
                else:
                    po.write({"origin": po.origin})
            else:
                po.write({"origin": origin})

        # <<< QTL Edit
        # We do not merge PO lines
        # Create Line
        # po_line = False
        # for line in po.order_line:
        #     if line.product_id == product_id and line.product_uom == product_id.uom_po_id: # noqa
        #         if line._merge_in_existing_line(product_id, product_qty, product_uom, location_id, name, origin, values): # noqa
        #             vals = self._update_purchase_order_line(
        #                 product_id, product_qty, product_uom, values, line, partner) # noqa
        #             po_line = line.write(vals)
        #             break
        # if not po_line:
        # >>> QTL Edit
        vals = self._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner
        )
        self.env["purchase.order.line"].sudo().create(vals)
        if order_line:
            order_line.sudo().write({"purchase_order_id": po.id})

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, supplier
    ):
        res = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier
        )
        res["quant_id"] = values.get("quant_id", False)
        res["price_unit"] = values.get("price_unit", False)
        return res

    def _make_po_get_domain(self, values, partner):
        domain = super(StockRule, self)._make_po_get_domain(values, partner)
        if values.get("currency_id", False):
            domain += (("currency_id", "=", values["currency_id"]),)
        return domain

    def _prepare_purchase_order(
        self, product_id, product_qty, product_uom, origin, values, partner
    ):
        res = super(StockRule, self)._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner
        )
        if values.get("currency_id", False):
            res["currency_id"] = values["currency_id"]
        return res
