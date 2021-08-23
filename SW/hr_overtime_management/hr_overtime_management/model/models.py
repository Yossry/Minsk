# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.multi
    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        if 'overtime_type' in vals:
            self.env.user.update_overtime_groups()
        return res

    

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'company_id' in vals :
            self.update_overtime_groups()
        return res
    
    def overtime_menu_id(self):
        menu_id = self.env.ref('hr_overtime_management.menu_hr_overtime_menuitem',False)
        return menu_id and menu_id.id or 0
    
    @api.multi
    def update_overtime_groups(self):
        group_id = self.env.ref('hr_overtime_management.overtime_menu_group',False)
        if group_id:
            for user_id in self:
                if  user_id.company_id.overtime_type != 'request':
                    self._cr.execute("delete from res_groups_users_rel where gid = %d and uid = %d"%(group_id.id,user_id.id))
                    self._cr.execute("insert into res_groups_users_rel values (%d , %d)"%(group_id.id,user_id.id))
#                     group_id.users = [(4,user_id.id)]
                else:
                    self._cr.execute("delete from res_groups_users_rel where gid = %d and uid = %d"%(group_id.id,user_id.id))
#                     group_id.users = [(3,user_id.id)]

    @classmethod
    def _login(cls, db, login, password):
        res  = super(ResUsers, cls)._login(db, login, password)
        if res:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user_id = self.browse(res)
                user_id.update_overtime_groups()
        return res
