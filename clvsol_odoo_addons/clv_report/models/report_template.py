# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportTemplate(models.Model):
    _description = 'Report Template'
    _name = 'clv.report.template'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Report Template Name'
    )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    model = fields.Char(
        string='Model',
        required=True,
        help="Model name of the object on which the report method to be called is located, e.g. 'res.partner'"
    )

    method = fields.Char(
        string='Method',
        required=True,
        help="Name of the method to be called when the report job is processed."
    )

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
    ]
