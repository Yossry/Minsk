# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Family(models.Model):
    _name = "clv.family"
    _inherit = 'clv.family', 'clv.abstract.code'

    code = fields.Char(string='Family Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.family.code')
