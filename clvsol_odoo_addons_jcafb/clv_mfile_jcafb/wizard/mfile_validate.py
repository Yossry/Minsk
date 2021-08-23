# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import xlrd
import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MfileValidate(models.TransientModel):
    _description = 'Media File Validate'
    _name = 'clv.mfile.validate'

    def _default_mfile_ids(self):
        return self._context.get('active_ids')
    mfile_ids = fields.Many2many(
        comodel_name='clv.mfile',
        relation='clv_mfile_mfile_validate_rel',
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
    def do_mfile_validate(self):
        self.ensure_one()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('id', '=', self.directory_id.id),
        ])

        SurveyQuestion = self.env['survey.question']

        for mfile in self.mfile_ids:

            filepath = file_system_directory.directory + '/' + mfile.name
            _logger.info(u'>>>>> %s', filepath)

            if mfile.state in ['checked', 'validated']:

                book = xlrd.open_workbook(filepath)
                sheet = book.sheet_by_index(0)
                survey_title = sheet.cell_value(0, 0)
                _logger.info(u'>>>>>>>>>> %s', survey_title)

                question_code = False
                question_type = False
                question_matrix_subtype = False
                matrix_row = False
                question_constr_mandatory = False
                question_comments_allowed = False
                response_count = 0

                prev_question_code = False
                prev_question_type = False
                prev_question_matrix_subtype = False
                prev_matrix_row = False
                prev_question_constr_mandatory = False
                # prev_question_comments_allowed = False
                # prev_response_count = 0

                begin_question = False
                end_question = False
                last_row = sheet.nrows - 1
                last_question_code = False

                _logger.info(u'>>>>>>>>>> %s', last_row)

                for i in range(sheet.nrows):

                    prev_question_code = question_code
                    prev_question_type = question_type
                    prev_question_matrix_subtype = question_matrix_subtype
                    prev_matrix_row = matrix_row
                    prev_question_constr_mandatory = question_constr_mandatory
                    # prev_question_comments_allowed = question_comments_allowed
                    # prev_response_count = response_count

                    code_row = sheet.cell_value(i, 0)

                    if code_row == xlrd.empty_cell.value:
                        continue

                    if code_row == '[]':
                        code_cols = {}
                        for k in range(sheet.ncols):
                            code_col = sheet.cell_value(i, k)
                            if code_col != xlrd.empty_cell.value:
                                code_cols.update({k: code_col})

                    row_code = code_row.replace('[', '').replace(']', '')

                    if len(row_code) < 11:
                        continue
                    else:
                        question_code = row_code[:11]
                        survey_question_search = SurveyQuestion.search([
                            ('code', '=', question_code),
                        ])
                        if survey_question_search.id is not False:
                            matrix_row = False
                            question_type = survey_question_search.type
                            question_constr_mandatory = survey_question_search.constr_mandatory
                            if question_type == 'matrix':
                                question_matrix_subtype = survey_question_search.matrix_subtype
                                question_comments_allowed = False
                            else:
                                question_matrix_subtype = False
                                question_comments_allowed = survey_question_search.comments_allowed
                            if question_type == 'matrix':
                                if question_code != row_code:
                                    matrix_row = True
                                    question_code = row_code
                                    if question_code != last_question_code:
                                        if question_code is not False and last_question_code is not False:
                                            end_question = True
                                        begin_question = True
                                        last_question_code = question_code
                        if question_code != last_question_code:
                            if question_code is not False and last_question_code is not False:
                                end_question = True
                            begin_question = True
                            last_question_code = question_code

                    if end_question is True:

                        if prev_question_constr_mandatory is True:
                            if prev_question_type in ['textbox', 'datetime']:
                                if response_count != 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + prev_question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + prev_question_code + ' sem resposta!'

                            if prev_question_type in ['simple_choice']:
                                if response_count == 0:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + prev_question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + prev_question_code + ' sem resposta!'
                                if response_count > 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + prev_question_code + ' com mais de uma resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + prev_question_code + ' com mais de uma resposta!'

                            if prev_question_type in ['multiple_choice']:
                                if response_count < 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + prev_question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + prev_question_code + ' sem resposta!'

                            if prev_question_type in ['matrix'] and prev_question_matrix_subtype in ['simple']:
                                if prev_matrix_row is True:
                                    if response_count == 0:
                                        if mfile.notes is False:
                                            mfile.notes = \
                                                u'Erro: Questão ' + prev_question_code + ' sem resposta!'
                                        else:
                                            mfile.notes += \
                                                u'\nErro: Questão ' + prev_question_code + ' sem resposta!'
                                    if response_count > 1:
                                        if mfile.notes is False:
                                            mfile.notes = \
                                                u'Erro: Questão ' + prev_question_code + ' com mais de uma resposta!'
                                        else:
                                            mfile.notes += \
                                                u'\nErro: Questão ' + prev_question_code + ' com mais de uma resposta!'

                        _logger.info(u'----------> %s %s %s', response_count, matrix_row, prev_matrix_row)
                        response_count = 0
                        end_question = False

                    if begin_question is True:
                        _logger.info(u'----------> %s %s %s %s %s %s %s',
                                     question_code, question_type, question_matrix_subtype, question_constr_mandatory,
                                     question_comments_allowed, matrix_row, prev_matrix_row)
                        begin_question = False

                    _logger.info(u'>>>>>>>>>> (%s) %s %s %s', code_row, row_code, question_code, last_question_code)

                    for j in range(sheet.ncols):

                        if sheet.cell_value(i, j) == '.':
                            try:
                                value = sheet.cell_value(i, j + 1)
                            except Exception:
                                value = xlrd.empty_cell.value
                            if value != xlrd.empty_cell.value:
                                if question_type in ['multiple_choice', 'simple_choice']:
                                    if question_code != row_code:
                                        response_count += 1
                                else:
                                    response_count += 1

                                question_code = row_code[:11]
                                survey_question_search = SurveyQuestion.search([
                                    ('code', '=', question_code),
                                ])
                                if survey_question_search.id is not False:
                                    question_parameter = survey_question_search.parameter

                                    if question_parameter == 'date':
                                        date = value
                                        try:
                                            datetime.datetime.strptime(value, '%Y-%m-%d')
                                        except Exception:
                                            try:
                                                date = datetime.datetime(
                                                    *xlrd.xldate_as_tuple(date, book.datemode)).strftime('%Y-%m-%d')
                                                value = date
                                            except Exception:
                                                try:
                                                    datetime.datetime.strptime(value, '%d-%m-%Y')
                                                except Exception:
                                                    if mfile.notes is False:
                                                        mfile.notes = \
                                                            u'Erro: Questão ' + \
                                                            question_code + ' com formato invalido!'
                                                    else:
                                                        mfile.notes += \
                                                            '\nErro: Questão ' + \
                                                            question_code + ' com formato invalido!'

                    if i == last_row or \
                       (i == last_row - 1 and sheet.cell_value(i + 1, 0) == xlrd.empty_cell.value):
                        end_question = True

                    if end_question is True:

                        if question_constr_mandatory is True:
                            if question_type in ['textbox', 'datetime']:
                                if response_count != 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + question_code + ' sem resposta!'

                            if question_type in ['simple_choice']:
                                if response_count == 0:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + question_code + ' sem resposta!'
                                if response_count > 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + question_code + ' com mais de uma resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + question_code + ' com mais de uma resposta!'

                            if question_type in ['multiple_choice']:
                                if response_count < 1:
                                    if mfile.notes is False:
                                        mfile.notes = \
                                            u'Erro: Questão ' + question_code + ' sem resposta!'
                                    else:
                                        mfile.notes += \
                                            u'\nErro: Questão ' + question_code + ' sem resposta!'

                            if question_type in ['matrix'] and question_matrix_subtype in ['simple']:
                                if matrix_row is True:
                                    if response_count == 0:
                                        if mfile.notes is False:
                                            mfile.notes = \
                                                u'Erro: Questão ' + question_code + ' sem resposta!'
                                        else:
                                            mfile.notes += \
                                                u'\nErro: Questão ' + question_code + ' sem resposta!'
                                    if response_count > 1:
                                        if mfile.notes is False:
                                            mfile.notes = \
                                                u'Erro: Questão ' + question_code + ' com mais de uma resposta!'
                                        else:
                                            mfile.notes += \
                                                u'\nErro: Questão ' + question_code + ' com mais de uma resposta!'

                        _logger.info(u'----------> %s %s %s', response_count, matrix_row, prev_matrix_row)
                        response_count = 0
                        end_question = False

                if mfile.notes is False:
                    mfile.state = 'validated'
                else:
                    mfile.state = 'returned'

        return True

    @api.multi
    def do_populate_all_mfiles(self):
        self.ensure_one()

        Mfile = self.env['clv.mfile']
        mfiles = Mfile.search([])

        self.mfile_ids = mfiles

        return self._reopen_form()
