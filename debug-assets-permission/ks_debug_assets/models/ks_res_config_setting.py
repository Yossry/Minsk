# -*- coding: utf-8 -*-

from odoo import fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_hide_debug_assets_permission = fields.Boolean(string='Hide Debug Assets', config_parameter='ks_hide_debug_assets_permission')