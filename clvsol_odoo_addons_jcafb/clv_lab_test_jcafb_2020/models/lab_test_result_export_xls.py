# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import xlwt
from xlutils.copy import copy
from xlrd import open_workbook

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestResult(models.Model):
    _name = "clv.lab_test.result"
    _inherit = 'clv.lab_test.result'

    def lab_test_result_export_xls(self, dir_path, file_name, use_template, template_dir_path):

        lab_test_type = self.lab_test_type_id.code
        lab_test_request_code = self.lab_test_request_id.code

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', dir_path),
        ])

        if use_template:
            template_file_name = file_name.replace('<type>', lab_test_type).replace('<request_code>', 'nnn.nnn-dd')
            template_file_path = template_dir_path + '/' + template_file_name
            book = open_workbook(template_file_path, formatting_info=True)
            wbook = copy(book)
            sheet = wbook.get_sheet(0)
            file_name = file_name.replace('<type>', lab_test_type).replace('<request_code>', lab_test_request_code)
            file_path = dir_path + '/' + file_name
            idx = book.sheet_names().index(template_file_name)
            wbook.get_sheet(idx).name = file_name
        else:
            file_name = file_name.replace('<type>', lab_test_type).replace('<request_code>', lab_test_request_code)
            file_path = dir_path + '/' + file_name
            wbook = xlwt.Workbook()
            sheet = wbook.add_sheet(file_name)

        _logger.info(u'%s %s %s %s', '>>>>>>>>>>', lab_test_request_code, lab_test_type, use_template)

        row_nr = 0

        save_book = False

        if lab_test_type == 'EAN20':
            self.lab_test_result_export_xls_EAN20(sheet, row_nr, use_template)
            save_book = True

        if lab_test_type == 'ECP20':
            self.lab_test_result_export_xls_ECP20(sheet, row_nr, use_template)
            save_book = True

        if lab_test_type == 'EDH20':
            self.lab_test_result_export_xls_EDH20(sheet, row_nr, use_template)
            save_book = True

        if lab_test_type == 'EEV20':
            self.lab_test_result_export_xls_EEV20(sheet, row_nr, use_template)
            save_book = True

        if lab_test_type == 'EUR20':
            self.lab_test_result_export_xls_EUR20(sheet, row_nr, use_template)
            save_book = True

        if lab_test_type == 'EAA20':
            self.lab_test_result_export_xls_EAA20(sheet, row_nr, use_template)
            save_book = True

        if save_book:

            wbook.save(file_path)

            self.directory_id = file_system_directory.id
            self.file_name = file_name
            self.stored_file_name = file_name

        return True
