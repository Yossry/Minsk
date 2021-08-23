# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_summary_files_directory", "clv.global_settings.current_summary_files_directory"),
    ("current_summary_file_name", "clv.global_settings.current_summary_file_name"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_summary_files_directory = fields.Char(
        string='Summary Files Directory',
        compute='_compute_current_summary_files_directory',
        store=False,
    )

    current_summary_file_name = fields.Char(
        string='Summary File Name',
        compute='_compute_current_summary_file_name',
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

    summary_files_directory = fields.Char(
        string='Summary Files Directory:'
    )

    summary_file_name = fields.Char(
        string='Summary File Name:'
    )

    @api.depends('summary_files_directory')
    def _compute_current_summary_files_directory(self):
        for r in self:
            r.current_summary_files_directory = r.summary_files_directory

    @api.depends('summary_file_name')
    def _compute_current_summary_file_name(self):
        for r in self:
            r.current_summary_file_name = r.summary_file_name

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_summary_files_directory = defaults['current_summary_files_directory']
        defaults['summary_files_directory'] = current_summary_files_directory

        current_summary_file_name = defaults['current_summary_file_name']
        defaults['summary_file_name'] = current_summary_file_name

        return defaults
