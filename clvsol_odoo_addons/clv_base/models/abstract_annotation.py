# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import *

from odoo import fields, models


class AbstractAnnotation(models.AbstractModel):
    _description = 'Abstract Annotation'
    _name = 'clv.abstract.annotation'
    _order = "date_annotation desc"

    name = fields.Char(string='Subject', index=True, required=False)
    author = fields.Many2one(
        comodel_name='res.users', string='Author', required=True, readonly=True,
        default=lambda self: self._uid
    )
    date_annotation = fields.Datetime(
        string="Annotation Date", required=True, readonly=True,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    body = fields.Text(string='Body')

    active = fields.Boolean(string='Active', default=True)
