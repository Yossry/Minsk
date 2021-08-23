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

    def lab_test_report_export_xls_EAA20(self, sheet, row_nr, logo_file_path, use_template):

        ExportXLS = self.env['clv.export_xls']

        lab_test_request_code = self.lab_test_request_id.code

        sheet.header_str = ''.encode()
        sheet.footer_str = ''.encode()

        for i in range(0, 49):
            sheet.col(i).width = 256 * 2
        sheet.show_grid = False

        sheet.insert_bitmap(logo_file_path, row_nr, 3)

        # Endereço:
        col_nr, row_nr = 7, 7
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.name)
        # Código do Endereço:
        col_nr, row_nr = 12, 8
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.ref_id.code)

        # Morador:
        col_nr, row_nr = 7, 10
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-01-01'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)
        # Código do Morador:
        col_nr, row_nr = 42, 10
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-01-02'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)

        # Data do Exame:
        col_nr, row_nr = 9, 11
        if self.date_approved is not False:
            date = datetime.strftime(self.date_approved, '%d-%m-%Y')
            ExportXLS.setOutCell(sheet, col_nr, row_nr, date)
        else:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, None)
        # Código do Exame:
        col_nr, row_nr = 42, 11
        ExportXLS.setOutCell(sheet, col_nr, row_nr, lab_test_request_code)

        # Local da coleta:
        col_nr, row_nr = 9, 16
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-02-01'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)
        # Ponto da coleta:
        col_nr, row_nr = 9, 18
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-02-02'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)
        # Data da coleta:
        col_nr, row_nr = 9, 20
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-02-03'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)

        # Cloro livre:
        col_nr, row_nr = 6, 25
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-03-01'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)
        # pH:
        col_nr, row_nr = 2, 32
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-03-04'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)

        # Coliformes totais:
        col_nr, row_nr = 9, 40
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-04-01'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)
        # Escherichia coli:
        col_nr, row_nr = 33, 40
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-04-04'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)

        # Observações:
        col_nr, row_nr = 7, 48
        criterion = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAA20-05-01'),
        ])
        if criterion.result is not False:
            ExportXLS.setOutCell(sheet, col_nr, row_nr, criterion.result)

        # Farmacêutico(a) Responsável (nome):
        col_nr, row_nr = 32, 58
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.name)
        # Farmacêutico(a) Responsável (CRF):
        col_nr, row_nr = 35, 59
        ExportXLS.setOutCell(sheet, col_nr, row_nr, self.employee_id.professional_id)

        return True
