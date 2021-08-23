# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AbstractModelExport(models.AbstractModel):
    _inherit = 'clv.abstract.model_export'

    def model_export_dir_path(self, export_type):
        filestore_path = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_filestore_path', '').strip()
        if export_type == 'csv':
            export_files_directory_csv = self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_export_files_directory_csv', '').strip()
            return filestore_path + '/' + export_files_directory_csv
        if export_type == 'sqlite':
            export_files_directory_sqlite = self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_export_files_directory_sqlite', '').strip()
            return filestore_path + '/' + export_files_directory_sqlite
        if export_type == 'xls':
            export_files_directory_xls = self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_export_files_directory_xls', '').strip()
            return filestore_path + '/' + export_files_directory_xls
        return False
