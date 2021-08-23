# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
# import xlwt
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestReport(models.Model):
    _name = "clv.lab_test.report"
    _inherit = 'clv.lab_test.report'

    def lab_test_report_export_xls_EDH20(self, sheet, row_nr, logo_file_path, use_template):

        ExportXLS = self.env['clv.export_xls']

        # lab_test_type = self.lab_test_type_id.code
        lab_test_request_code = self.lab_test_request_id.code
        # lab_test_result_code = self.code

        sheet.header_str = ''.encode()
        sheet.footer_str = ''.encode()

        for i in range(0, 49):
            sheet.col(i).width = 256 * 2
        sheet.show_grid = False

        # row_nr += 2

        sheet.insert_bitmap(logo_file_path, row_nr, 3)

        # Nome:
        col_nr, row_nr = 6, 7
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.name)
        # Cadastro:
        col_nr, row_nr = 39, 7
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.code)

        # Data do Exame:
        col_nr, row_nr = 10, 9
        if self.date_approved is not False:
            date = datetime.strftime(self.date_approved, '%d-%m-%Y')
            ExportXLS.setOutCell(sheet, col_nr, row_nr, date)
        else:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, None)
        # Código do Exame:
        col_nr, row_nr = 42, 9
        ExportXLS.setOutCell(sheet, col_nr, row_nr, lab_test_request_code)

        # Glicose:
        col_nr, row_nr = 7, 18
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-04-01'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + ' mg/dL')

        # Colesterol total:
        col_nr, row_nr = 10, 28
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-04-05'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + ' mg/dL')

        # PAS:
        col_nr, row_nr = 10, 41
        result_pas = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-03-06'),
        ]).result
        if result_pas is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_pas)
        # PAD:
        col_nr, row_nr = 13, 41
        result_pad = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-03-07'),
        ]).result
        if result_pad is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_pad)

        # Peso:
        col_nr, row_nr = 5, 52
        result_peso = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-02-01'),
        ]).result
        if result_peso is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_peso + u' kg')
        # Altura:
        col_nr, row_nr = 15, 52
        result_altura = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-02-03'),
        ]).result
        if result_altura is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_altura + u' cm')
        # IMC:
        col_nr, row_nr = 25, 52
        result_imc = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-02-05'),
        ]).result
        if result_imc is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_imc + u' kg/m²')
        # Circunferência abdominal:
        col_nr, row_nr = 44, 52
        result_circunf = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-02-09'),
        ]).result
        if result_circunf is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result_circunf + u' cm')

        # Observações:
        col_nr, row_nr = 9, 54
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-05-01'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result)

        # Farmacêutico(a) Responsável (Nome):
        col_nr, row_nr = 31, 62
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.name)
        # Farmacêutico(a) Responsável (ID):
        col_nr, row_nr = 35, 63
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.professional_id)

        row_nr += 1
        page_break_1 = row_nr

        sheet.insert_bitmap(logo_file_path, row_nr, 3)

        # Nome:
        col_nr, row_nr = 6, 72
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.name)
        # Cadastro:
        col_nr, row_nr = 39, 72
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.code)

        # Data do Exame:
        col_nr, row_nr = 10, 74
        if self.date_approved is not False:
            date = datetime.strftime(self.date_approved, '%d-%m-%Y')
            ExportXLS.setOutCell(sheet, col_nr, row_nr, date)
        else:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, None)
        # Código do Exame:
        col_nr, row_nr = 42, 74
        ExportXLS.setOutCell(sheet, col_nr, row_nr, lab_test_request_code)

        # Colesterol total:
        col_nr, row_nr = 10, 79
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-06-01'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + u' mg/dL')

        # HDL-colesterol:
        col_nr, row_nr = 10, 84
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-06-04'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + u' mg/dL')

        # HLDL-colesterol:
        col_nr, row_nr = 10, 89
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-06-07'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + u' mg/dL')

        # Fração não HDL:
        col_nr, row_nr = 10, 94
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-06-08'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + u' mg/dL')

        # Triglicérides:
        col_nr, row_nr = 9, 102
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-07-01'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result + u' mg/dL')

        # Observações:
        col_nr, row_nr = 9, 107
        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EDH20-08-02'),
        ]).result
        if result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, result)

        # Farmacêutico(a) Responsável (Nome):
        col_nr, row_nr = 31, 134
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.name)
        # Farmacêutico(a) Responsável (ID):
        col_nr, row_nr = 35, 135
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.professional_id)

        sheet.horz_page_breaks = [
            (page_break_1, 0, 255),
        ]

        return True
