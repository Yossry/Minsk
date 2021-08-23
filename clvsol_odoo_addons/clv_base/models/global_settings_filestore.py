# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_filestore_path", "clv.global_settings.current_filestore_path"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_filestore_path = fields.Char(
        string='File Store Path',
        compute='_compute_current_filestore_path',
        store=False,
    )

    @api.multi
    def set_values(self):
        self.ensure_one()

        super().set_values()

        for field_name, key_name in PARAMS:
            value = str(getattr(self, field_name, '')).strip()
            self.env['ir.config_parameter'].set_param(key_name, value)

    def get_values(self):

        res = super().get_values()

        for field_name, key_name in PARAMS:
            res[field_name] = self.env['ir.config_parameter'].get_param(key_name, '').strip()
        return res


class GlobalSettings_2(models.TransientModel):
    _inherit = 'clv.global_settings'

    filestore_path = fields.Char(
        string='File Store Path:'
    )

    @api.depends('filestore_path')
    def _compute_current_filestore_path(self):
        for r in self:
            r.current_filestore_path = r.filestore_path

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_filestore_path = defaults['current_filestore_path']
        defaults['filestore_path'] = current_filestore_path

        return defaults
