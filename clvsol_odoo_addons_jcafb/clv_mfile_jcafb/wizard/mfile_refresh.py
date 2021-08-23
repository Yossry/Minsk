# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import datetime
import xlrd

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def modification_date(filepath):
    t = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(t)


class MfileRefresh(models.TransientModel):
    _description = 'Media File Refresh'
    _name = 'clv.mfile.refresh'

    def _default_mfile_ids(self):
        return self._context.get('active_ids')
    mfile_ids = fields.Many2many(
        comodel_name='clv.mfile',
        relation='clv_mfile_mfile_refresh_rel',
        string='Media Files',
        default=_default_mfile_ids
    )

    def _default_directory_id(self):
        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('name', '=', 'Survey Files (Input)'),
        ])
        directory_id = file_system_directory.id
        return directory_id
    directory_id = fields.Many2one(
        comodel_name='clv.file_system.directory',
        string='Directory',
        default=_default_directory_id,
        required="True"
    )

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_mfile_refresh(self):
        self.ensure_one()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('id', '=', self.directory_id.id),
        ])

        SurveyQuestion = self.env['survey.question']

        listdir = os.listdir(file_system_directory.directory)

        for mfile in self.mfile_ids:

            _logger.info(u'%s %s', '>>>>>', mfile.name)

            if mfile.name in listdir:

                filepath = file_system_directory.directory + '/' + mfile.name
                _logger.info(u'%s %s', '>>>>>>>>>>', filepath)

                # mfile.directory_id = file_system_directory.id
                # mfile.file_name = mfile.name
                # mfile.stored_file_name = mfile.name

                if mfile.state in ['new', 'returned', 'checked', 'validated']:

                    mfile.state = 'checked'
                    mfile.code = False
                    mfile.person_code = False
                    mfile.family_code = False
                    mfile.address_code = False
                    mfile.notes = False
                    mfile.document_id = False

                    book = xlrd.open_workbook(filepath)
                    sheet = book.sheet_by_index(0)
                    survey_title = sheet.cell_value(0, 0)
                    mfile.survey_title = survey_title

                    mfile.date_file = modification_date(filepath)

                    document_code = False
                    person_code = False
                    family_code = False
                    address_code = False

                    for i in range(sheet.nrows):

                        code_row = sheet.cell_value(i, 0)

                        if code_row == '[]':
                            code_cols = {}
                            for k in range(sheet.ncols):
                                code_col = sheet.cell_value(i, k)
                                if code_col != xlrd.empty_cell.value:
                                    code_cols.update({k: code_col})
                        row_code = code_row.replace('[', '').replace(']', '')

                        for j in range(sheet.ncols):

                            if sheet.cell_value(i, j) != xlrd.empty_cell.value:

                                if sheet.cell_value(i, j) == '.':
                                    try:
                                        value = sheet.cell_value(i, j + 1)
                                    except Exception:
                                        value = xlrd.empty_cell.value
                                    if value != xlrd.empty_cell.value:

                                        question_code = row_code[:11]
                                        survey_question_search = SurveyQuestion.search([
                                            ('code', '=', question_code),
                                        ])
                                        if survey_question_search.id is not False:
                                            question_parameter = survey_question_search.parameter

                                            if question_parameter == 'document_code':
                                                document_code = value
                                                mfile.code = document_code

                                            if question_parameter == 'person_code':
                                                person_code = value
                                                mfile.person_code = person_code

                                            if question_parameter == 'family_code':
                                                family_code = value
                                                mfile.family_code = family_code

                                            if question_parameter == 'address_code':
                                                address_code = value
                                                mfile.address_code = address_code

                if document_code is not False:

                    Document = self.env['clv.document']
                    document = Document.search([
                        ('code', '=', document_code),
                    ])

                    if document.code != document_code:
                        mfile.state = 'returned'
                        if mfile.notes is False:
                            mfile.notes = u'Erro: Código do Documento inválido!'
                        else:
                            mfile.notes += u'\nErro: Código do Documento inválido!'

                    else:

                        mfile.document_id = document.id

                        if document.survey_id.title != survey_title:
                            mfile.state = 'returned'
                            if mfile.notes is False:
                                mfile.notes = u'Erro: Tipo de Questionário inconsistente com o Documento!'
                            else:
                                mfile.notes += u'\nErro: Tipo de Questionário inconsistente com o Documento!'

                        if mfile.name != mfile.document_id.name + '_' + mfile.document_id.code + '.xls':

                            mfile.state = 'returned'
                            if mfile.notes is False:
                                mfile.notes = u'Erro: Nome do Documento inválido!!'
                            else:
                                mfile.notes += u'\nErro: Nome do Documento inválido!!'

                        if person_code is not False:

                            if document.ref_id.code != person_code:
                                mfile.state = 'returned'
                                if mfile.notes is False:
                                    mfile.notes = u'Erro: Código da Pessoa inválido!'
                                else:
                                    mfile.notes += u'\nErro: Código da Pessoa inválido!'
                        if family_code is not False:

                            if document.ref_id.code != family_code:
                                mfile.state = 'returned'
                                if mfile.notes is False:
                                    mfile.notes = u'Erro: Código da Família inválido!'
                                else:
                                    mfile.notes += u'\nErro: Código da Família inválido!'
                        if address_code is not False:

                            if document.ref_id.code != address_code:
                                mfile.state = 'returned'
                                if mfile.notes is False:
                                    mfile.notes = u'Erro: Código do Endereço inválido!'
                                else:
                                    mfile.notes += u'\nErro: Código ddo Endereço inválido!'

            else:

                if mfile.state in ['new', 'returned', 'checked', 'validated']:

                    # mfile.directory_id = False
                    # mfile.file_name = False
                    # mfile.stored_file_name = False

                    mfile.state = 'new'
                    mfile.code = False
                    mfile.person_code = False
                    mfile.family_code = False
                    mfile.address_code = False
                    mfile.notes = False
                    mfile.document_id = False

        return True

    @api.multi
    def do_populate_all_mfiles(self):
        self.ensure_one()

        Mfile = self.env['clv.mfile']
        mfiles = Mfile.search([])

        self.mfile_ids = mfiles

        return self._reopen_form()
