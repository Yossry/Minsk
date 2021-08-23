# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class GlobalSettings(models.TransientModel):
    _description = 'Global Settings'
    _name = 'clv.global_settings'
    _inherit = 'res.config.settings'
