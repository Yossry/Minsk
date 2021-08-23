# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    owner_id = fields.Many2one(
        "res.partner",
        "Owner",
        help="This is the owner of the quant",
        readonly=True,
        select=True,
        required=True,
    )

    @api.model
    def create(self, vals):
        """Set the owner based on the location.

        This is not a default method because we need to know the location.

        """
        if not vals.get("owner_id"):
            Company = self.env["res.company"]
            location = self.env["stock.location"].browse(vals["location_id"])
            vals["owner_id"] = (
                location.partner_id.id
                or location.company_id.partner_id.id
                or Company.browse(
                    Company._company_default_get("stock.quant").id
                ).partner_id.id
            )
        return super(StockQuant, self).create(vals)

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        if not owner_id:
            owner_id = location_id.partner_id or location_id.company_id.partner_id
        return super(StockQuant, self)._gather(
            product_id, location_id, lot_id, package_id, owner_id, strict
        )
