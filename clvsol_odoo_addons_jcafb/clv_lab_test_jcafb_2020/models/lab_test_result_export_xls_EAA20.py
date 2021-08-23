# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
# import xlwt
from datetime import datetime
import pytz

from odoo import models

_logger = logging.getLogger(__name__)


class LabTestResult(models.Model):
    _name = "clv.lab_test.result"
    _inherit = 'clv.lab_test.result'

    def lab_test_result_export_xls_EAA20(self, sheet, row_nr, use_template):

        # user_tz = self.env.user.tz
        user_tz = 'America/Argentina/Buenos_Aires'
        local = pytz.timezone(user_tz)
        date_received_utc = pytz.utc.localize(self.lab_test_request_id.date_received)
        date_received_local = date_received_utc.astimezone(local)
        date_received_local_str = datetime.strftime(date_received_local, '%d-%m-%Y %H:%M:%S')

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
            ExportXLS.setOutCell(sheet, 12, row_nr, lab_test_type + ' - ' + u'ANÁLISE DE ÁGUA - RESULTADO')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Endereço:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Endereço:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.code)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Morador:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Morador:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Local da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Ponto da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Responsável pela Coleta:')
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
                date_received_local_str
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 5, row_nr, u'Determinação de Cloro Livre (Cl) e pH')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Cloro Livre (mg/L):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'pH:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 20

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 30

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            row_nr += 1
            ExportXLS.setOutCell(sheet, 5, row_nr, u'Análise Microbiótica')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Coliformes totais:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Escherichia coli:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 20

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 30

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 2

        else:

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 12, row_nr, lab_test_type + ' - ' + u'ANÁLISE DE ÁGUA - RESULTADO')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código da Requisição:')
            ExportXLS.setOutCell(sheet, 10, row_nr, lab_test_request_code)
            ExportXLS.setOutCell(sheet, 33, row_nr, u'Código do Resultado:')
            ExportXLS.setOutCell(sheet, 43, row_nr, lab_test_result_code)
            row_nr += 1

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Endereço:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.name)
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Endereço:')
            ExportXLS.setOutCell(sheet, 10, row_nr, self.ref_id.code)
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Morador:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Código do Morador:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Local da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Ponto da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Data da Coleta:')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Responsável pela Coleta:')
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
                date_received_local_str
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 5, row_nr, u'Determinação de Cloro Livre (Cl) e pH')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Cloro Livre (mg/L):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'pH:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 20

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 30

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            row_nr += 1
            ExportXLS.setOutCell(sheet, 5, row_nr, u'Análise Microbiótica')
            row_nr += 2

            ref_row_nr = row_nr

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Coliformes totais:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Escherichia coli:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 20

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Data:')
            row_nr += 2

            row_nr = ref_row_nr
            delta = 30

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável:')
            row_nr += 2

            row_nr += 1
            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 2

        return True
