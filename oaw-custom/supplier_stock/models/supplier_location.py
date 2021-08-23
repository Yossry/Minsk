# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SupplierLocation(models.Model):
    _name = "supplier.location"
    _description = "Partner Location"
    _order = "name"

    short_loc = fields.Char("Location", readonly=True)
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    supplier_lead_time = fields.Integer(string="Partner Lead Time (Days)")
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        help="Default currency to be proposed in Supplier Stock records.",
    )
    owner_id = fields.Many2one(string="Owner", comodel_name="res.partner")
    hk_location = fields.Boolean(string="HK Location", default=False)

    _sql_constraints = [
        (
            "name_supp_location_uniq",
            "unique(name)",
            "The name of the supplier location must be unique!",
        )
    ]

    @api.model
    def create(self, vals):
        to_shorten = vals["name"]
        splits = to_shorten.split(" ")
        vals["short_loc"] = splits[1] if len(splits) > 1 else vals["name"]
        return super(SupplierLocation, self).create(vals)

    @api.multi
    def write(self, vals):
        if "name" in vals:
            to_shorten = vals["name"]
            splits = to_shorten.split(" ")
            vals["short_loc"] = splits[1] if len(splits) > 1 else vals["name"]
        return super(SupplierLocation, self).write(vals)
