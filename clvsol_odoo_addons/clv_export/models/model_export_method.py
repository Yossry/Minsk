# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ModelExportMethod(models.Model):
    _description = 'Model Export Method'
    _name = 'clv.model_export.method'
    _order = 'name'

    name = fields.Char(
        string='Model',
        required=True,
        help="Model name of the object to be used when the exportation job is processed, e.g. 'res.partner'"
    )

    export_type = fields.Selection(
        [('xls', 'XLS'),
         ('csv', 'CSV'),
         ('sqlite', 'SQLite'),
         ], string='Export Type', default='', readonly=False, required=True
    )

    method = fields.Char(
        string='Method',
        required=True,
        help="Name of the method to be called when the exportation job is processed."
    )

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (export_type, name)',
         u'Error! The Name for a Export Type must be unique!'),
    ]
