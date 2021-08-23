# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    supplier_code = fields.Char("Code", related="supplier_id.ref", store=True)
    is_shipment = fields.Boolean("Shipment")

    @api.model
    def create(self, vals):
        if "is_mto" in vals and vals["is_mto"]:
            user = self.env.user
            if user.has_group("supplier_user_access.group_supplier"):
                # If Supplier creates a MTO, it will be declared as is_shipment
                vals["is_shipment"] = True
                # If Supplier creates a MTO, supplier_id is set accordingly
                vals["supplier_id"] = self.env.user.partner_id.id
            # If internal user creates MTO, user will required to set a Sales
            # Supplier
            if not user.has_group("supplier_user_access.group_supplier"):
                if "supplier_id" in vals:
                    if not vals["supplier_id"]:
                        raise UserError(
                            _("For MTO a Sales Supplier has to be selected!")
                        )
        return super(SaleOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.is_mto:
                user = self.env.user
                # If Supplier creates a MTO, it will be declared as is_shipment
                if user.has_group("supplier_user_access.group_supplier"):
                    vals["is_shipment"] = True
                # If internal user creates MTO, user will required to set a
                # Sales Supplier
                if not user.has_group("supplier_user_access.group_supplier"):
                    if "supplier_id" in vals:
                        if not vals["supplier_id"]:
                            raise UserError(
                                _("For MTO a Sales Supplier has to be selected!")
                            )
        return super(SaleOrder, self).write(vals)
