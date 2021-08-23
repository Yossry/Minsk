# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_export_files_directory_csv", "clv.global_settings.current_export_files_directory_csv"),
    ("current_export_files_directory_sqlite", "clv.global_settings.current_export_files_directory_sqlite"),
    ("current_export_files_directory_xls", "clv.global_settings.current_export_files_directory_xls"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_export_files_directory_csv = fields.Char(
        string='Export Files Directory (CSV)',
        compute='_compute_current_export_files_directory_csv',
        store=False,
    )

    current_export_files_directory_sqlite = fields.Char(
        string='Export Files Directory (SQLite)',
        compute='_compute_current_export_files_directory_sqlite',
        store=False,
    )

    current_export_files_directory_xls = fields.Char(
        string='Export Files Directory (XLS)',
        compute='_compute_current_export_files_directory_xls',
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

    export_files_directory_csv = fields.Char(
        string='Export Files Directory (CSV):'
    )

    export_files_directory_sqlite = fields.Char(
        string='Export Files Directory (SQLite):'
    )

    export_files_directory_xls = fields.Char(
        string='Export Files Directory (XLS):'
    )

    @api.depends('export_files_directory_csv')
    def _compute_current_export_files_directory_csv(self):
        for r in self:
            r.current_export_files_directory_csv = r.export_files_directory_csv

    @api.depends('export_files_directory_sqlite')
    def _compute_current_export_files_directory_sqlite(self):
        for r in self:
            r.current_export_files_directory_sqlite = r.export_files_directory_sqlite

    @api.depends('export_files_directory_xls')
    def _compute_current_export_files_directory_xls(self):
        for r in self:
            r.current_export_files_directory_xls = r.export_files_directory_xls

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_export_files_directory_csv = defaults['current_export_files_directory_csv']
        defaults['export_files_directory_csv'] = current_export_files_directory_csv

        current_export_files_directory_sqlite = defaults['current_export_files_directory_sqlite']
        defaults['export_files_directory_sqlite'] = current_export_files_directory_sqlite

        current_export_files_directory_xls = defaults['current_export_files_directory_xls']
        defaults['export_files_directory_xls'] = current_export_files_directory_xls

        return defaults
