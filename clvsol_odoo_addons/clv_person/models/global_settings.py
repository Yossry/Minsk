# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_date_reference", "clv.global_settings.current_date_reference"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_date_reference = fields.Date(
        string='Reference Date',
        compute='_compute_current_date_reference',
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

    date_reference = fields.Date(string="Reference Date:")

    @api.depends('date_reference')
    def _compute_current_date_reference(self):
        for r in self:
            r.current_date_reference = r.date_reference

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_date_reference = defaults['current_date_reference']
        defaults['date_reference'] = current_date_reference

        return defaults
