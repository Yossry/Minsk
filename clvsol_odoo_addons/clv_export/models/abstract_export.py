# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import *

from odoo import fields, models


class AbstractExport(models.AbstractModel):
    _description = 'Abstract Export'
    _name = 'clv.abstract.export'

    name = fields.Char(string='Name', index=True, required=True)

    label = fields.Char(string='Label')

    date_export = fields.Datetime(
        string="Export Date", required=True, readonly=True,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=True)
