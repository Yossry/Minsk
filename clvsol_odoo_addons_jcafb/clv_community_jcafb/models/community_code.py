# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Community(models.Model):
    _name = "clv.community"
    _inherit = 'clv.community', 'clv.code.model'

    code = fields.Char(string='Community Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.community.code')
