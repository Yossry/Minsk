# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryTemplate(models.Model):
    _description = 'Summary Template'
    _name = 'clv.summary.template'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Summary Template Name'
    )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    model = fields.Char(
        string='Model',
        required=True
    )

    # method = fields.Char(
    #     string='Method',
    #     required=True,
    #     help="Name of the method to be called when the summary job is processed."
    # )

    action = fields.Char(
        string='Action',
        required=False,
        help="Name of the action used to process the summary."
    )

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
    ]
