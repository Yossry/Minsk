# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.addons.base.models.res_users import get_selection_groups


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        group_obj = self.env['res.groups']
        groups_by_application = group_obj.sudo().get_groups_by_application()

        def find_implied(group):
            # Recusively find all implied groups
            res = []
            for implied in group.implied_ids:
                res.append(implied)
                for item in implied:
                    res += find_implied(item)
            return res

        def update_implied(implied):
            res = {}
            for item in implied:
                for category, ttype, groups in groups_by_application:  # pylint: disable=W0612
                    if ttype == 'boolean' and \
                       item.id in [g.id for g in groups]:
                        res.update({'in_group_%s' % item.id: False})
            return res

        to_upd = {}
        for key, value in vals.items():  # pylint: disable=W0612
            if key.startswith('sel_groups_'):
                groups = get_selection_groups(key)
                for group in group_obj.browse(groups):
                    implied = find_implied(group)
                    to_upd.update(update_implied(implied))
        vals.update(to_upd)
        return super(ResUsers, self).write(vals)
