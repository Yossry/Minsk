# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestReportExportXLS(models.TransientModel):
    _description = 'Lab Test Report Export XLS'
    _name = 'clv.lab_test.report.export_xls'

    def _default_lab_test_report_ids(self):
        return self._context.get('active_ids')
    lab_test_report_ids = fields.Many2many(
        comodel_name='clv.lab_test.report',
        relation='clv_lab_test_report_export_xls_rel',
        string='Lab Test Reports',
        default=_default_lab_test_report_ids
    )

    def _default_dir_path_report(self):
        file_store_path = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_filestore_path', '').strip()
        lab_test_report_files_directory_xls = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_lab_test_report_files_directory_xls', '').strip()
        return file_store_path + '/' + lab_test_report_files_directory_xls
    dir_path_report = fields.Char(
        string='Directory Path (Report)',
        required=True,
        help="Directory Path (Report)",
        default=_default_dir_path_report
    )

    def _default_file_name_report(self):
        lab_test_report_file_name_xls = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_lab_test_report_file_name_xls', '').strip()
        return lab_test_report_file_name_xls
    file_name_report = fields.Char(
        string='File Name (Report)',
        required=True,
        help="File Name (Report)",
        default=_default_file_name_report
    )

    use_template_report = fields.Boolean(string='Use Template (Report)', default=True)

    def _default_templates_dir_path_report(self):
        file_store_path = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_filestore_path', '').strip()
        lab_test_report_files_directory_templates = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_lab_test_report_files_directory_templates', '').strip()
        return file_store_path + '/' + lab_test_report_files_directory_templates
    templates_dir_path_report = fields.Char(
        string='Template Directory Path (Report)',
        required=True,
        help="Template Directory Path (Report)",
        default=_default_templates_dir_path_report
    )

    @api.multi
    def do_lab_test_report_export_xls(self):
        self.ensure_one()

        for lab_test_report_reg in self.lab_test_report_ids:

            _logger.info(u'%s %s', '>>>>>', lab_test_report_reg.code)

            lab_test_report_reg.lab_test_report_export_xls(self.dir_path_report, self.file_name_report,
                                                           self.use_template_report, self.templates_dir_path_report)

        return True
