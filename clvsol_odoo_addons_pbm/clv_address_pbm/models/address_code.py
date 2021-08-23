# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Address(models.Model):
    _name = "clv.address"
    _inherit = 'clv.address', 'clv.abstract.code'

    code = fields.Char(string='Address Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.address.code')
