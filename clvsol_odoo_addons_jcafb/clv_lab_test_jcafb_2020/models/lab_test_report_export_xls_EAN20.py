# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from xlwt import easyxf
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestReport(models.Model):
    _name = "clv.lab_test.report"
    _inherit = 'clv.lab_test.report'

    def lab_test_report_export_xls_EAN20(self, sheet, row_nr, logo_file_path, use_template):

        ExportXLS = self.env['clv.export_xls']

        bottom_border = easyxf('border: bottom thin')

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
        ExportXLS.setOutCell(sheet, 19, row_nr, u'JCAFB-2019 - FERNÃO - SP')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 17, row_nr,
                             u'Centro Acadêmico de Farmácia-Bioquímica')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 18, row_nr,
                             u'Faculdade de Ciências Farmacêuticas')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 20, row_nr, u'Universidade de São Paulo')
        row_nr += 1

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Nome:')
        # ExportXLS.setOutCell(sheet, 4, row_nr, self.person_id.name)
        ExportXLS.setOutCell(sheet, 6, row_nr, self.ref_id.name)
        ExportXLS.setOutCell(sheet, 30, row_nr, u'Cadastro:')
        # ExportXLS.setOutCell(sheet, 35, row_nr, self.person_id.code)
        ExportXLS.setOutCell(sheet, 35, row_nr, self.ref_id.code)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Data do Exame:')
        if self.date_approved is not False:
            date = datetime.strftime(self.date_approved, '%d-%m-%Y')
            ExportXLS.setOutCell(sheet, 9, row_nr, date)
        else:
            ExportXLS.setOutCell(sheet, 9, row_nr, None)
        ExportXLS.setOutCell(sheet, 30, row_nr, u'Código do Exame:')
        ExportXLS.setOutCell(sheet, 38, row_nr, lab_test_request_code)
        row_nr += 1

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 13, row_nr, u'CAMPANHA PARA DETECÇÃO DE ANEMIA')
        row_nr += 1

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 15, row_nr, u'DETERMINAÇÃO DE HEMOGLOBINA')
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Material: Sangue total/EDTA')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Método utilizado: Automatizado - equipamento Micros 60, Horiba-ABX')
        row_nr += 3

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Resultado:')
        row_nr += 2

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAN20-02-03'),
        ]).result
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Valor da Hemoglobina (g/dL):')
        if result is not False:
            ExportXLS.setOutCell(sheet, 16, row_nr, result)
        row_nr += 2

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Informações complementares')
        row_nr += 2

        result_peso = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAN20-01-01'),
        ]).result
        result_altura = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAN20-01-03'),
        ]).result
        # result_circunf = self.criterion_ids.search([
        #     ('lab_test_report_id', '=', self.id),
        #     ('code', '=', 'EAN20-01-05'),
        # ]).result
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Peso:')
        if result_peso is not False:
            ExportXLS.setOutCell(sheet, 5, row_nr, result_peso)
        ExportXLS.setOutCell(sheet, 8, row_nr, 'kg')
        ExportXLS.setOutCell(sheet, 14, row_nr, 'Altura:')
        if result_altura is not False:
            ExportXLS.setOutCell(sheet, 18, row_nr, result_altura)
        ExportXLS.setOutCell(sheet, 22, row_nr, u'cm')
        # ExportXLS.setOutCell(sheet, 27, row_nr, u'Circunferência abdominal:')
        # if result_circunf is not False:
        #     ExportXLS.setOutCell(sheet, 39, row_nr, result_circunf)
        # ExportXLS.setOutCell(sheet, 43, row_nr, u'cm')
        row_nr += 4

        result = self.criterion_ids.search([
            ('lab_test_report_id', '=', self.id),
            ('code', '=', 'EAN20-02-06'),
        ]).result
        ExportXLS.setOutCell(sheet, 2, row_nr, u'Observações:')
        if result is not False:
            ExportXLS.setOutCell(sheet, 9, row_nr, result)
        row_nr += 1

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 2

        ExportXLS.setOutCell(sheet, 14, row_nr, u'VALORES DE REFERÊNCIA - HEMOGLOBINA')
        row_nr += 2

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Idade')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'Hemoglobina (g/dL)')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'Idade')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'Hemoglobina (g/dL)')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'0 dia (cordão)')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'13,5 - 19,5')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'0,5 a 2 anos')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'10,5 - 13,5')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'1 a 3 dias')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'14,5 - 22,5')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'2 a 6 anos')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'11,5 - 13,5')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'4 a 14 dias')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'13,5 - 21,5')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'6 a 12 anos')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'11,5 - 15,5')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'15 a 29 dias')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'12,5 - 20,5')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'12 a 18 anos - F')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'12,0 - 16,0')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'30 dias (1 mês)')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'10,0 - 18,0')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'12 a 18 anos - M')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'13,0 - 16,0')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'2 meses')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'  9,0 - 14,0')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'Adulto - F')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'12,0 - 16,0')
        row_nr += 1
        ExportXLS.setOutCell(sheet, 2, row_nr, u'3 a 6 meses')
        ExportXLS.setOutCell(sheet, 12, row_nr, u'  9,5 - 13,5')
        ExportXLS.setOutCell(sheet, 26, row_nr, u'Adulto - M')
        ExportXLS.setOutCell(sheet, 38, row_nr, u'13,5 - 17,5')
        row_nr += 1

        for i in range(0, 49):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 1

        ExportXLS.setOutCell(sheet, 2, row_nr, u'Valores de Referência segundo Wintrobe, 12 ed., 2009.')
        row_nr += 1

        row_nr += 8

        ExportXLS.setOutCell(sheet, 17, row_nr, u'Farmacêutico(a) Responsável:')
        for i in range(30, 48):
            sheet.write(row_nr, i, style=bottom_border)
        row_nr += 1
        ExportXLS.setOutCell(sheet, 33, row_nr, self.employee_id.name)
        row_nr += 1
        ExportXLS.setOutCell(sheet, 36, row_nr, self.employee_id.professional_id)

        return True
