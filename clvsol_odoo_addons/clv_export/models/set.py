# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ModelExport(models.Model):
    _inherit = 'clv.model_export'

    code = fields.Char(string='Model Export Code', required=False)

    export_set_elements = fields.Boolean(string='Export Set Elements', default=False)

    export_set_id = fields.Many2one(
        comodel_name='clv.set',
        string='Set',
        ondelete='restrict'
    )
    count_export_set_elements = fields.Integer(
        string='Set Elements (count)',
        compute='_compute_count_export_set_elements',
        store=False
    )

    @api.depends('export_set_id')
    def _compute_count_export_set_elements(self):
        for r in self:
            r.count_export_set_elements = len(r.export_set_id.set_element_ids)
