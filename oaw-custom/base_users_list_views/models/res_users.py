# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    is_supplier = fields.Boolean(
        related="partner_id.supplier", readonly=True, store=True
    )
    is_customer = fields.Boolean(
        related="partner_id.customer", readonly=True, store=True
    )
    show_password = fields.Char(readonly=True, String="Password")
    is_timecheck_light_date = fields.Datetime(string="Is TCL Since", default=False)
    is_timecheck_light = fields.Boolean(string="TCL Paid")
    has_supplier_access = fields.Boolean(
        string="Has Supplier Access", compute="compute_has_supplier_access", store=True
    )

    @api.multi
    @api.depends("groups_id")
    def compute_has_supplier_access(self):
        for user in self:
            user.has_supplier_access = (
                True if user.has_group("supplier_user_access.group_supplier") else False
            )

    # object action for chrono update button in sale order form view
    @api.multi
    def action_view_user_open(self):
        view_id = self.env.ref("base.view_users_form").id
        return {
            "name": "Supplier Users",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "res.users",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "target": "current",
        }

    def _set_password(self):
        ctx = self._crypt_context()
        for user in self:
            self._set_password_again(user.id, user.password)
            self._set_encrypted_password(user.id, ctx.encrypt(user.password))

    def _set_password_again(self, id, pwd):
        self.env.cr.execute(
            "UPDATE res_users SET show_password=%s WHERE id=%s", [pwd, id]
        )

    @api.multi
    def write(self, vals):
        if "is_timecheck_light" in vals and vals["is_timecheck_light"]:
            vals["is_timecheck_light_date"] = fields.datetime.now()
        return super(ResUsers, self).write(vals)

    def action_assign_supplier(self):
        vals = {}
        # Assign internal group to the user
        user_types_group_name = self.get_security_group_field_name(
            "base.module_category_user_type"
        )
        internal_user_group_field_value = self.env.ref("base.group_user").id
        vals[user_types_group_name] = internal_user_group_field_value
        # Assign supplier group to the user
        supplier_group_name = self.get_security_group_field_name(
            "supplier_user_access.module_category_supplier"
        )
        supplier_group_field_value = self.env.ref(
            "supplier_user_access.group_supplier"
        ).id
        vals[supplier_group_name] = supplier_group_field_value
        # Remove timecheck group from the user
        supplier_group_name = self.get_security_group_field_name(
            "website_timecheck.module_category_timecheck"
        )
        vals[supplier_group_name] = False
        return self.write(vals)
