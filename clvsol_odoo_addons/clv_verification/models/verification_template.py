# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VerificationTemplate(models.Model):
    _description = 'Verification Template'
    _name = 'clv.verification.template'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Verification Template Name'
    )

    # verification_max_task = fields.Integer(
    #     string='Max Task Registers'
    # )

    # verification_disable_identification = fields.Boolean(
    #     string='Disable Identification'
    # )

    # verification_disable_check_missing = fields.Boolean(
    #     string='Disable Check Missing'
    # )

    # verification_disable_inclusion = fields.Boolean(
    #     string='Disable Inclusion'
    # )

    # verification_disable_verification = fields.Boolean(
    #     string='Disable Verification'
    # )

    # verification_last_update_start = fields.Datetime(
    #     string="Last Update (Start)"
    # )

    # verification_last_update_end = fields.Datetime(
    #     string="Last Update (End)"
    # )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    model = fields.Char(
        string='Model',
        required=True,
        help="Model name of the object on which the verification method to be called is located, e.g. 'res.partner'"
    )

    # method = fields.Char(
    #     string='Method',
    #     required=True,
    #     help="Name of the method to be called when the verification job is processed."
    # )

    action = fields.Char(
        string='Action',
        required=False,
        help="Name of the action used to process the verification."
    )

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
    ]
