# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import *

from odoo import fields, models


class FamilyHistory(models.Model):
    _description = 'Family History'
    _name = 'clv.family.history'
    _order = "date_sign_in desc"

    date_sign_in = fields.Date(
        string='Sign in date',
        required=False,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d')
    )
    date_sign_out = fields.Date(
        string="Sign out date",
        required=False
    )

    active = fields.Boolean(string='Active', default=1)
