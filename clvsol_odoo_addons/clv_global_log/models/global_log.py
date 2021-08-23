# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class GlobalLog(models.Model):
    _description = 'Global Log'
    _name = 'clv.global_log'
    _inherit = 'clv.abstract.log'
