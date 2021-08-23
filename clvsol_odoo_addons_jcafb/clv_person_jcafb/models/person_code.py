# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Person(models.Model):
    _name = "clv.person"
    _inherit = 'clv.person', 'clv.abstract.code'

    code = fields.Char(string='Person Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.person.code')
