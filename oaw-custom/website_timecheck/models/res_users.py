# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    timecheck_group = fields.Selection(
        [
            ("group_timecheck_trial", "Trial"),
            ("group_timecheck_basic", "Basic"),
            ("group_timecheck_light", "Light"),
        ],
        string="Groups",
    )

    def get_security_group_field_name(self, group_category_xml_id):
        for app, _kind, gs in self.env["res.groups"].get_groups_by_application():
            module_category = self.env.ref(group_category_xml_id)
            if app == module_category:
                return "sel_groups_" + "_".join(map(str, map(int, gs)))

    def action_assign_timecheck(self):
        self.update({"timecheck_group": "group_timecheck_trial"})

    @api.multi
    def write(self, vals):
        timecheck_group_name = self.get_security_group_field_name(
            "website_timecheck.module_category_timecheck"
        )
        # Assign Timecheck group by timecheck_group
        if "timecheck_group" in vals:
            # Assign Portal group to the user
            user_types_group_name = self.get_security_group_field_name(
                "base.module_category_user_type"
            )
            portal_group_field_value = self.env.ref("base.group_portal").id
            vals[user_types_group_name] = portal_group_field_value
            # Assign the selected Timecheck group to the user
            timecheck_group_field_value = (
                self.env.ref("website_timecheck.%s" % vals["timecheck_group"]).id
                if vals["timecheck_group"]
                else False
            )
            vals[timecheck_group_name] = timecheck_group_field_value
        return super(ResUsers, self).write(vals)
