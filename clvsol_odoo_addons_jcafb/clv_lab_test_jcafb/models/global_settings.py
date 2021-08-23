# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_lab_test_result_files_directory_xls",
        "clv.global_settings.current_lab_test_result_files_directory_xls"),
    ("current_lab_test_result_file_name_xls",
        "clv.global_settings.current_lab_test_result_file_name_xls"),
    ("current_lab_test_result_files_directory_templates",
        "clv.global_settings.current_lab_test_result_files_directory_templates"),
    ("current_lab_test_report_files_directory_xls",
        "clv.global_settings.current_lab_test_report_files_directory_xls"),
    ("current_lab_test_report_file_name_xls",
        "clv.global_settings.current_lab_test_report_file_name_xls"),
    ("current_lab_test_report_files_directory_templates",
        "clv.global_settings.current_lab_test_report_files_directory_templates"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_lab_test_result_files_directory_xls = fields.Char(
        string='Lab Test Result Files Directory (XLS)',
        compute='_compute_current_lab_test_result_files_directory_xls',
        store=False,
    )

    current_lab_test_result_file_name_xls = fields.Char(
        string='Lab Test Result File Name (XLS)',
        compute='_compute_current_lab_test_result_file_name_xls',
        store=False,
    )

    current_lab_test_result_files_directory_templates = fields.Char(
        string='Lab Test Result Files Directory (Templates)',
        compute='_compute_current_lab_test_result_files_directory_templates',
        store=False,
    )

    current_lab_test_report_files_directory_xls = fields.Char(
        string='Lab Test Report Files Directory (XLS)',
        compute='_compute_current_lab_test_report_files_directory_xls',
        store=False,
    )

    current_lab_test_report_file_name_xls = fields.Char(
        string='Lab Test Report File Name (XLS)',
        compute='_compute_current_lab_test_report_file_name_xls',
        store=False,
    )

    current_lab_test_report_files_directory_templates = fields.Char(
        string='Lab Test Report Files Directory (Templates)',
        compute='_compute_current_lab_test_report_files_directory_templates',
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

    lab_test_result_files_directory_xls = fields.Char(
        string='Lab Test Result Files Directory (XLS):'
    )

    lab_test_result_file_name_xls = fields.Char(
        string='Lab Test Result File Name (XLS):'
    )

    lab_test_result_files_directory_templates = fields.Char(
        string='Lab Test Result Files Directory (Templates):'
    )

    lab_test_report_files_directory_xls = fields.Char(
        string='Lab Test Report Files Directory (XLS):'
    )

    lab_test_report_file_name_xls = fields.Char(
        string='Lab Test Report File Name (XLS):'
    )

    lab_test_report_files_directory_templates = fields.Char(
        string='Lab Test Report Files Directory (Templates):'
    )

    @api.depends('lab_test_result_files_directory_xls')
    def _compute_current_lab_test_result_files_directory_xls(self):
        for r in self:
            r.current_lab_test_result_files_directory_xls = r.lab_test_result_files_directory_xls

    @api.depends('lab_test_result_file_name_xls')
    def _compute_current_lab_test_result_file_name_xls(self):
        for r in self:
            r.current_lab_test_result_file_name_xls = r.lab_test_result_file_name_xls

    @api.depends('lab_test_result_files_directory_templates')
    def _compute_current_lab_test_result_files_directory_templates(self):
        for r in self:
            r.current_lab_test_result_files_directory_templates = r.lab_test_result_files_directory_templates

    @api.depends('lab_test_report_files_directory_xls')
    def _compute_current_lab_test_report_files_directory_xls(self):
        for r in self:
            r.current_lab_test_report_files_directory_xls = r.lab_test_report_files_directory_xls

    @api.depends('lab_test_report_file_name_xls')
    def _compute_current_lab_test_report_file_name_xls(self):
        for r in self:
            r.current_lab_test_report_file_name_xls = r.lab_test_report_file_name_xls

    @api.depends('lab_test_report_files_directory_templates')
    def _compute_current_lab_test_report_files_directory_templates(self):
        for r in self:
            r.current_lab_test_report_files_directory_templates = r.lab_test_report_files_directory_templates

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        current_lab_test_result_files_directory_xls = \
            defaults['current_lab_test_result_files_directory_xls']
        defaults['lab_test_result_files_directory_xls'] = current_lab_test_result_files_directory_xls

        current_lab_test_result_file_name_xls = \
            defaults['current_lab_test_result_file_name_xls']
        defaults['lab_test_result_file_name_xls'] = current_lab_test_result_file_name_xls

        current_lab_test_report_files_directory_xls = \
            defaults['current_lab_test_report_files_directory_xls']
        defaults['lab_test_report_files_directory_xls'] = current_lab_test_report_files_directory_xls

        current_lab_test_result_files_directory_templates = \
            defaults['current_lab_test_result_files_directory_templates']
        defaults['lab_test_result_files_directory_templates'] = current_lab_test_result_files_directory_templates

        current_lab_test_report_file_name_xls = \
            defaults['current_lab_test_report_file_name_xls']
        defaults['lab_test_report_file_name_xls'] = current_lab_test_report_file_name_xls

        current_lab_test_report_files_directory_templates = \
            defaults['current_lab_test_report_files_directory_templates']
        defaults['lab_test_report_files_directory_templates'] = current_lab_test_report_files_directory_templates

        return defaults
