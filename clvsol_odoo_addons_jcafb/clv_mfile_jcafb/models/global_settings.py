# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_survey_files_directory_archive", "clv.global_settings.current_survey_files_directory_archive"),
    ("current_survey_files_directory_input", "clv.global_settings.current_survey_files_directory_input"),
    ("current_survey_files_directory_templates", "clv.global_settings.current_survey_files_directory_templates"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_survey_files_directory_archive = fields.Char(
        string='Survey Files Directory (Archive)',
        compute='_compute_current_survey_files_directory_archive',
        store=False,
    )

    current_survey_files_directory_input = fields.Char(
        string='Survey Files Directory (Input)',
        compute='_compute_current_survey_files_directory_input',
        store=False,
    )

    current_survey_files_directory_templates = fields.Char(
        string='Survey Files Directory (Templates)',
        compute='_compute_current_survey_files_directory_templates',
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

    survey_files_directory_archive = fields.Char(
        string='Survey Files Directory (Archive):'
    )

    survey_files_directory_input = fields.Char(
        string='Survey Files Directory (Input):'
    )

    survey_files_directory_templates = fields.Char(
        string='Survey Files Directory (Templates):'
    )

    @api.depends('survey_files_directory_archive')
    def _compute_current_survey_files_directory_archive(self):
        for r in self:
            r.current_survey_files_directory_archive = r.survey_files_directory_archive

    @api.depends('survey_files_directory_input')
    def _compute_current_survey_files_directory_input(self):
        for r in self:
            r.current_survey_files_directory_input = r.survey_files_directory_input

    @api.depends('survey_files_directory_templates')
    def _compute_current_survey_files_directory_templates(self):
        for r in self:
            r.current_survey_files_directory_templates = r.survey_files_directory_templates

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_survey_files_directory_archive = defaults['current_survey_files_directory_archive']
        defaults['survey_files_directory_archive'] = current_survey_files_directory_archive

        current_survey_files_directory_input = defaults['current_survey_files_directory_input']
        defaults['survey_files_directory_input'] = current_survey_files_directory_input

        current_survey_files_directory_templates = defaults['current_survey_files_directory_templates']
        defaults['survey_files_directory_templates'] = current_survey_files_directory_templates

        return defaults
