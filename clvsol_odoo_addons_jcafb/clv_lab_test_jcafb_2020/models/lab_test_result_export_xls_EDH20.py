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

    def lab_test_result_export_xls_EDH20(self, sheet, row_nr, use_template):

        # todo:
        # Make data_hours GMT aware.
        delta_hours = -3

        ExportXLS = self.env['clv.export_xls']

        lab_test_type = self.lab_test_type_id.code
        lab_test_request_code = self.lab_test_request_id.code
        lab_test_result_code = self.code
        # lab_test_result_has_complement = self.has_complement

        sheet.header_str = ''.encode()
        sheet.footer_str = ''.encode()

        for i in range(0, 49):
            sheet.col(i).width = 256 * 2
        sheet.show_grid = False

        if use_template:

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE DHC - Resultados (1)')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Exames complementares?')
            # ExportXLS.setOutCell(sheet, 14, row_nr, lab_test_result_has_complement)
            ExportXLS.setOutCell(sheet, 15, row_nr, u'Sim')
            ExportXLS.setOutCell(sheet, 20, row_nr, u'Não')
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
            ExportXLS.setOutCell(sheet, 25, row_nr, u'Data do Recebimento:')
            ExportXLS.setOutCell(
                sheet, 35, row_nr,
                (self.lab_test_request_id.date_received + timedelta(hours=delta_hours)).strftime('%d-%m-%Y  %H:%M:%S')
            )
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr,
                                 u'Tempo de Jejum:')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(sheet, 4, row_nr, u'a) Menor que 8 hs')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'd) Não sabe')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 4, row_nr, u'b) Entre 8 e 12 hs')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'e) Não quis responder')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 4, row_nr, u'c) Maior que 12 hs')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'f) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Medidas Antropométricas')
            row_nr += 2
            delta = 24

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Peso (kg):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Altura (cm):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'IMC (=Peso/(Altura x Altura)) (kg/m²):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (IMC):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de IMC (OMS; Adultos.: 19 a 64 anos; Idosos:igual ou maior a 65 anos):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Baixo peso (Adultos:menor que 18,5; Idosos (M e F): menor que 21,9)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Peso Normal (Adultos: 18,5 a 24,9; Idosos (M e F): 22,0 a 27,0)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Sobrepeso (Pré-obeso) (Adultos: 25,0 a 29,9; Idosos(M): 27,1 a 30,0/Idosos(F): 27,1 a 32,0)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Obesidade Grau I (Adultos: 30,0 a 34,9; Idosos(M): 30,1,1 a 35,0/Idosos(F): 32,1 a 37,0)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Obesidade Grau II (Adultos: 35,0 a 39,9; Idosos(M): 35,1 a 39,0/Idosos(F): 37,1 a 41,9)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'f) Obesidade Grau III (Adultos:maior ou igual a 40,0; Idosos(M):maior ou igual a 40,0/')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 14, row_nr,
                u'Idosos(F):maior ou igual a 42,0)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'g) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'h) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Circunferência Abdominal (cm):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de Circunferência Abdominal (ABESO; Adultos):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Normal (H:menor que 94 cm; M:menor que 80 cm)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Risco aumentado (H:maior ou igual a 94 cm; M:maior ou igual a 80 cm)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Risco aumentado substancialmente (H:maior ou igual a 102 cm; M:maior ou igual a 88 cm)))')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Não interpretado (justificar em observações)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            # row = sheet.row(row_nr)
            # for i in range(0, 49):
            #     row.write(i, u'-')
            # row_nr += 2

            page_break_1 = row_nr

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE DHC - Resultados (2)')
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

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Pressão Arterial')
            row_nr += 2
            delta = 24

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Pressão arterial automática (mmHg):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Pressão arterial manual (mmHg):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'PAS (mmHg):')
            ExportXLS.setOutCell(sheet, 15, row_nr, u'PAD (mmHg):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de Pressão Arterial (VII Diretriz Brasileira de Hipertensão Arterial - 2016):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Normal (PAS menor ou igual a 120 mmHg e PAD menor ou igual a 80 mmHg)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Pré-hipertensão (PAS:131-139 mmHg e PAD:81-89 mmHg)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Hipertensão estágio 1 (PAS:140-159 mmHg e PAD:90-99 mmHg)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Hipertensão estágio 2 (PAS:160-179 mmHg e PAD:100-109 mmHg)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Hipertensão estágio 3 (PAS:maior ou igual a 180 mmHg e PAD:maior ou igual a 110 mmHg)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'f) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'g) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Glicemia e Colesterolemia')
            row_nr += 2
            delta = 24

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Glicemia (mg/dL):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de Glicemia  (Diretrizes Sociedade Brasileira de Diabetes (2017-2018):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Normal para jejum de 8-12 hs(menor ou igual a 99 mg/dL)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Pré-diabetes (para jejum de 8-12 hs) = risco aumentado para diabetes (100-125 mg/dL)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Diabetes - para jejum de 8-12 hs (maior que 126 mg/dL, )')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Jejum INFERIOR a 8 hs: Normal (até 140 mg/dL)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Jejum INFERIOR a 8 hs: Aumentado (maior ou igual a 140 mg/dL)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'f) Não avaliado (justificar)')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'g) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Outras situações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Colesterol (mg/dL):')
            ExportXLS.setOutCell(sheet, delta, row_nr, u'Responsável (medida):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de Colesterol ')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'(atualização da Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose-2017):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Desejável:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 4

            # row = sheet.row(row_nr)
            # for i in range(0, 49):
            #     row.write(i, u'-')
            # row_nr += 2

            page_break_2 = row_nr

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE DHC - Resultados (3)')
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

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Colestorol Total + Frações')
            row_nr += 2
            delta = 24

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Colesterol total (mg/dL):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de Colesterol')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'(atualização da Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose-2017):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Desejável:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'HDL-Colesterol (mg/dL):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de HDL-Colesterol')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'(atualização da Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose-2017):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Desejável:Acima de 20 anos: maior que 40 mg/dL;2-19 anos: maior que 45 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Baixo: Acima de 20 anos: menor ou igual a 40 mg/dL;2-19 anos: menor ou igual a 45 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Leitura não realizada pelo equipamento')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'LDL-Colesterol (mg/dL):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Frações não HDL (mg/dL):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação do valor de LDL-Colesterol e Fração não HDL')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'(atualização da Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose-2017):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) A interpretação dos resultados deverá considerar a categoria de risco cardiovascular do paciente,')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 5, row_nr,
                u'e esta deve ser analisada pelo médico')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Leitura não realizada pelo equipamento')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            # row = sheet.row(row_nr)
            # for i in range(0, 49):
            #     row.write(i, u'-')
            # row_nr += 2

            page_break_3 = row_nr

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE DHC - Resultados (4)')
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

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Triglicérides')
            row_nr += 2
            delta = 24

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Triglicérides (mg/dL):')
            row_nr += 2

            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'Interpretação de Triglicérides')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 1, row_nr,
                u'(atualização da Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose-2017):')
            row_nr += 2
            delta = 22

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'a) Desejável:Acima de 20 anos:menor que 150 mg/dL;10-19 anos:menor que 190 mg/dL;')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 5, row_nr,
                u'0-9 anos:menor que 75 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'b) Alto: Acima de 20 anos:maior ou igual a 150 mg/dL;2-19 anos:maior ou igual a 190 mg/dL;')
            row_nr += 1
            ExportXLS.setOutCell(
                sheet, 5, row_nr,
                u'0-9 anos:maior ou igual a 75 mg/dL')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'c) Leitura não realizada pelo equipamento')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'd) Não interpretado (justificar em "Observações")')
            row_nr += 1

            ExportXLS.setOutCell(
                sheet, 4, row_nr,
                u'e) Não se aplica')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 4, row_nr, u'Observações:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Responsável (medidas):')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 0, row_nr, u'Observações:')
            row_nr += 6

            page_break_4 = row_nr

            sheet.horz_page_breaks = [
                (page_break_1, 0, 255),
                (page_break_2, 0, 255),
                (page_break_3, 0, 255),
                (page_break_4, 0, 255),
            ]

        else:

            ExportXLS.setOutCell(sheet, 17, row_nr, u'JCAFB-2020 - FERNÃO - SP')
            row_nr += 1
            ExportXLS.setOutCell(sheet, 8, row_nr, lab_test_type + ' - ' +
                                 u'CAMPANHA PARA DETECÇÃO DE DHC - Resultados')
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

            ExportXLS.setOutCell(sheet, 0, row_nr, u'IMC')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'IMC:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Responsável pela medida do IMC:')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Interpretação do valor de IMC:')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'a) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'b) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'c) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'd) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'e) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'f) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'g) ')
            row_nr += 1

            ExportXLS.setOutCell(sheet, 2, row_nr, u'h) ')
            row_nr += 2

            ExportXLS.setOutCell(sheet, 1, row_nr, u'Observações (IMC):')
            row_nr += 1

            row = sheet.row(row_nr)
            for i in range(0, 49):
                row.write(i, u'-')
            row_nr += 2

        return True
