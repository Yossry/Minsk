# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ModelExportTemplate(models.Model):
    _name = "clv.model_export.template"
    _inherit = 'clv.model_export.template', 'clv.abstract.code'

    code = fields.Char(string='Model Export Template Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.export.code')
