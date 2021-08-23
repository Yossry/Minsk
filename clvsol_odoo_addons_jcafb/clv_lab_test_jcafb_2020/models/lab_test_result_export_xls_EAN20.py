# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
# import xlwt
from datetime import timedelta

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestResult(models.Model):
    _name = "clv.lab_test.result"
    _inherit = 'clv.lab_test.result'

    def lab_test_result_export_xls_EAN20(self, sheet, row_nr, use_template):

        # todo:
        # Make data_hours GMT aware.
        delta_hours = -3

        ExportXLS = self.env['clv.export_xls']

        lab_test_type = self.lab_test_type_id.code
        lab_test_request_code = self.lab_test_request_id.code
        lab_test_result_code = self.code

        sheet.header_str = ''.encode()
        sheet.footer_str = ''.encode()

        for i in range(0, 49):
            sheet.col(i).width = 256 * 2
        sheet.show_grid = False

        if use_template:

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE ANEMIA - Resultados')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 11, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 35, row_nr, lab_test_result_code)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 11, row_nr, self.ref_id.name)
            row_nr += 2
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 11, row_nr, self.ref_id.code)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 11, row_nr, self.lab_test_request_id.employee_id.name)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 11, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 11, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Peso e Altura')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Peso (kg):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Altura (cm):')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 22

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida)')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Dosagem de Hemoglobina')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Horário da coleta:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Valor da Hemoglobina (g/dL):')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 22

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (coleta):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (dosagem):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr,
                                 u'Interpretação do Resultado de Hemoglobina (Wintrobe, 12ª ed., 2009):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'a) Normal')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'b) Abaixo no normal (anemia)')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'c) Acima do normal')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            # row = sheet.row(row_nr)
            # for i in range(0, 49):
            #     row.write(i, u'-')
            # row_nr += 2

        else:

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE ANEMIA - Resultados')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.code)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 10, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Peso')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Peso:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Responsável pela medida do Peso:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Altura')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Altura:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Responsável pela medida da Altura')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Hemoglobina')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Horário da coleta:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Responsável pela coleta:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Valor da Hemoglobina:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Responsável pela dosagem:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Interpretação do Resultado de Hemoglobina:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'a) Normal')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'b) Abaixo no normal (anemia)')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'c) Acima do normal')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Observações:')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 2

        return True
