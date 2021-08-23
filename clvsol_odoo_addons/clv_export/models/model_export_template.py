# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import exceptions


class ModelExportTemplate(models.Model):
    _description = 'Model Export Template'
    _name = 'clv.model_export.template'
    _inherit = 'clv.abstract.model_export'

    code = fields.Char(string='Model Export Template Code', required=False)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]

    @api.multi
    def copy(self):
        raise exceptions.ValidationError('It is not possible to duplicate the record, please create a new one.')
