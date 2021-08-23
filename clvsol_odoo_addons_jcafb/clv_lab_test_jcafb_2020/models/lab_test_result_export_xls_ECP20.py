# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
# import xlwt
from datetime import datetime, timedelta

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestResult(models.Model):
    _name = "clv.lab_test.result"
    _inherit = 'clv.lab_test.result'

    def lab_test_result_export_xls_ECP20(self, sheet, row_nr, use_template):

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

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 10, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 10, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 10, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

        else:

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            date_time = datetime.strptime(self.lab_test_request_id.date_received,
                                          '%Y-%m-%d %H:%M:%S') + timedelta(hours=delta_hours)
            date_time = datetime.strftime(date_time, '%d-%m-%Y  %H:%M:%S')
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(sheet, 10, row_nr, date_time)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            date_time = datetime.strptime(self.lab_test_request_id.date_received,
                                          '%Y-%m-%d %H:%M:%S') + timedelta(hours=delta_hours)
            date_time = datetime.strftime(date_time, '%d-%m-%Y  %H:%M:%S')
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(sheet, 10, row_nr, date_time)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'JCAFB-2020 - FERNÃO (SP) - ' + lab_test_type + ' - ' +
                                 u'EXAME COPROPARASITOLÓGICO - RESULTADOS')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Nome da Pessoa:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código da Pessoa:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.ref_id.code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Recebido por:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.lab_test_request_id.employee_id.name)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Recebedor:')
            ExportXLS.setOutCell(sheet, 43, row_nr, self.lab_test_request_id.employee_id.code)
            row_nr += 1
            date_time = datetime.strptime(self.lab_test_request_id.date_received,
                                          '%Y-%m-%d %H:%M:%S') + timedelta(hours=delta_hours)
            date_time = datetime.strftime(date_time, '%d-%m-%Y  %H:%M:%S')
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(sheet, 10, row_nr, date_time)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Método Utilizado:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 3

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Analisador(a):')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Revisado por:')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Resultado Confirmado (   )')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado Alterado (   )')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Digitado por::')
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Resultado digitado em:')
            row_nr += 1

        return True
