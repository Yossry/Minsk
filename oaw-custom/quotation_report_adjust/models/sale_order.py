# Copyright 2020 Timeware Limited & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_ref_report = fields.Char(string="Code on PDF", store=True)
    quot_report_note = fields.Text("Notes on PDF")

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # For quotation adjust: set new order_ref field
        if "name" in vals and "partner_id" in vals:
            # Get the reference number number
            fragments_order_ref = vals["name"].split("-")
            sub_order_ref = fragments_order_ref[-1]
            # Get the partner id
            domain = [("id", "=", vals["partner_id"])]
            partner_id = self.env["res.partner"].search(domain)
            partner_ref = partner_id.ref
            # New reference
            if not partner_ref:
                partner_ref = partner_id.name
            res.order_ref_report = sub_order_ref + " " + partner_ref
        return res
