# -*- coding: utf-8 -*-
from . import model
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    manu_id = env.ref('hr_overtime_management.menu_hr_overtime_menuitem')
    env.ref('hr_overtime_management.overtime_menu_rule').domain_force = "[('id','!=',%d)]" % manu_id.id