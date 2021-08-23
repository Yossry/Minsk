# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MediaFile(models.Model):
    _inherit = 'clv.mfile'

    date_file = fields.Datetime(
        string='File Date',
        readonly=True
    )

    survey_title = fields.Char(
        string='Survey Title',
        readonly=True
    )

    person_code = fields.Char(
        string='Person Code',
        readonly=True
    )

    family_code = fields.Char(
        string='Family Code',
        readonly=True
    )

    address_code = fields.Char(
        string='Address Code',
        readonly=True
    )

    _sql_constraints = [
        (
            'name_uniq',
            'UNIQUE (name)',
            'Error! The File Name must be unique!'
        ),
    ]
