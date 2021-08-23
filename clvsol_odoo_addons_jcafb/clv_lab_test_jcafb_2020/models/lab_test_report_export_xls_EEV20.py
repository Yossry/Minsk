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

    def lab_test_report_export_xls_EEV20(self, sheet, row_nr, logo_file_path, use_template):

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

        ExportXLS.setOutCell(sheet, 13, row_nr, u'Jornada Científica dos Acadêmicos de Farmácia-Bioquímica')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 19, row_nr, u'JCAFB-2020 - FERNÃO - SP')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 17, row_nr,
                             u'Centro Acadêmico de Farmácia-Bioquímica')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 18, row_nr,
                             u'Faculdade de Ciências Farmacêuticas')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 20, row_nr, u'Universidade de São Paulo')
        row_nr += 3

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Nome:')
        ExportXLS.setOutCell(sheet, 6, row_nr, self.ref_id.name)
        ExportXLS.setOutCell(sheet, 30, row_nr, u'Cadastro:')
        ExportXLS.setOutCell(sheet, 35, row_nr, self.ref_id.code)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Data do Exame:')
        if self.date_approved is not False:
            date = datetime.strftime(self.date_approved, '%d-%m-%Y')
            ExportXLS.setOutCell(sheet, 10, row_nr, date)
        else:
            ExportXLS.setOutCell(sheet, 10, row_nr, None)
        ExportXLS.setOutCell(sheet, 30, row_nr, u'Código do Exame:')
        ExportXLS.setOutCell(sheet, 38, row_nr, lab_test_request_code)
        row_nr += 7

        ExportXLS.setOutCell(sheet, 15, row_nr, u'PESQUISA DE')
        ExportXLS.setOutCell(sheet, 23, row_nr, u'Enterobius vermicularis')
        row_nr += 9

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EEV20-01-03'),
        ]).result
        ExportXLS.setOutCell(sheet, 18, row_nr, u'Resultado:')
        if result is not False:
            ExportXLS.setOutCell(sheet, 23, row_nr, result)
        row_nr += 11

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EEV20-01-05'),
        ]).result
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Métodos utilizados:')
        if result is not False:
            ExportXLS.setOutCell(sheet, 12, row_nr, result)
        row_nr += 2

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EEV20-01-03'),
        ]).normal_range
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Valor de referência:')
        ExportXLS.setOutCell(sheet, 12, row_nr, result)
        row_nr += 2

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EEV20-01-06'),
        ]).result
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Observações:')
        if result is not False:
            ExportXLS.setOutCell(sheet, 9, row_nr, result)
        row_nr += 14

        ExportXLS.setOutCell(sheet, 17, row_nr, u'Farmacêutico(a) Responsável:')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 33, row_nr, self.employee_id.name)
        row_nr += 1
        ExportXLS.setOutCell(sheet, 36, row_nr, self.employee_id.professional_id)

        return True
