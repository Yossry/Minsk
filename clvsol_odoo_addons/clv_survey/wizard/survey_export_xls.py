# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import xlwt

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SurveyExportXLS(models.TransientModel):
    _description = 'Survey Export XLS'
    _name = 'clv.survey.export_xls'

    def _default_survey_ids(self):
        return self._context.get('active_ids')
    survey_ids = fields.Many2many(
        comodel_name='survey.survey',
        relation='clv_survey_export_xls_rel',
        string='Surveys',
        default=_default_survey_ids
    )

    def _default_dir_path(self):
        dir_path = \
            self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_filestore_path', '').strip() + \
            '/' + \
            self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_survey_files_directory_templates', '').strip()

        return dir_path
    dir_path = fields.Char(
        string='Directory Path',
        required=True,
        help="Directory Path",
        default=_default_dir_path
    )

    file_name = fields.Char(
        string='File Name',
        required=True,
        help="File Name",
        default='<code>_nnn.nnn-dd_<file_format>.xls'
    )

    password = fields.Char(
        string='Password',
        required=True,
        help="Password to protec the sheet",
        default='OpenSesame'
    )

    file_format = fields.Selection(
        [('draft', 'Draft'),
         ('preformatted', 'Preformatted'),
         ], string='File Format', default='draft'
    )

    @api.multi
    def do_survey_export_xls(self):
        self.ensure_one()

        style_text_locked = xlwt.easyxf('''
            border: bottom THIN;
        ''')

        style_text_unlocked = xlwt.easyxf('''
            border: bottom THIN;
            protection: cell_locked false;
            font: bold on;
        ''')

        style_choice_thin = xlwt.easyxf('''
            font: bold on;
            borders: left THIN, right THIN, top THIN, bottom THIN;
            align: vertical center, horizontal center;
            protection: cell_locked false;
        ''')

        style_choice_dotted = xlwt.easyxf('''
            font: bold on;
            borders: left DOTTED, right DOTTED, top DOTTED, bottom DOTTED;
            align: vertical center, horizontal center;
            protection: cell_locked false;
        ''')

        style_dot = xlwt.easyxf('''
            align: vertical center, horizontal right;
        ''')

        isHidden = False
        if self.file_format == 'preformatted':
            isHidden = True

        for survey_reg in self.survey_ids:

            file_path = self.dir_path + '/' + \
                self.file_name.replace('<code>', survey_reg.code).replace('<file_format>', self.file_format)

            _logger.info(u'%s %s', '>>>>>', file_path)

            book = xlwt.Workbook()

            _title_ = survey_reg.title
            _description_ = survey_reg.description.replace('<p>', '').replace('</p>', '')

            row_nr = 0
            sheet = book.add_sheet(survey_reg.code)
            row = sheet.row(row_nr)
            row.write(0, '[' + survey_reg.code + ']')
            row_nr += 1

            row = sheet.row(row_nr)
            row.write(0, '[' + survey_reg.code + ']')
            row.write(2, _title_)
            row_nr += 1
            row = sheet.row(row_nr)
            row.write(0, '[' + survey_reg.code + ']')
            row.write(2, _description_)
            row_nr += 2

            for page in survey_reg.page_ids:

                _title_ = page.title
                _description_ = page.description.replace('<p>', '').replace('</p>', '')

                row = sheet.row(row_nr)
                row.write(0, '[' + page.code + ']')
                row.write(3, _title_)
                row_nr += 1
                row = sheet.row(row_nr)
                row.write(0, '[' + page.code + ']')
                row.write(3, _description_)
                row_nr += 2

                for question in page.question_ids:

                    _type_ = question.type
                    _question_ = question.question
                    if question.comments_message is not False:
                        _comments_message_ = question.comments_message
                    if question.comments_allowed is False:
                        _comments_message_ = ''

                    if _type_ == 'free_text' or _type_ == 'textbox' or _type_ == 'datetime':

                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _question_)
                        row_nr += 1
                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _type_)
                        row.hidden = isHidden
                        row_nr += 2
                        if _type_ == 'free_text':
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_text_unlocked)
                            for i in range(6, 15):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 1
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_text_unlocked)
                            for i in range(6, 15):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 1
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_text_unlocked)
                            for i in range(6, 15):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 1
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_text_unlocked)
                            for i in range(6, 15):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 1
                        else:
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(4, '.', style=style_dot)

                            row.write(5, None, style=style_text_unlocked)
                            for i in range(6, 15):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 1
                        row_nr += 1

                    if _type_ == 'simple_choice':

                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _question_)
                        row_nr += 1
                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _type_)
                        row.hidden = isHidden
                        row_nr += 2

                        for label in question.labels_ids:

                            _value_ = label.value

                            row = sheet.row(row_nr)
                            row.write(0, '[' + label.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_choice_thin)
                            row.write(6, _value_)
                            row_nr += 1

                        if question.comments_allowed is True:
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(6, _comments_message_)
                            row_nr += 2
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(6, '.', style=style_dot)
                            row.write(7, None, style=style_text_unlocked)
                            for i in range(8, 17):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 2
                        else:
                            row_nr += 1

                    if _type_ == 'multiple_choice':

                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _question_)
                        row_nr += 1
                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _type_)
                        row.hidden = isHidden
                        row_nr += 2

                        for label in question.labels_ids:

                            _value_ = label.value

                            row = sheet.row(row_nr)
                            row.write(0, '[' + label.code + ']')
                            row.write(4, '.', style=style_dot)
                            row.write(5, None, style=style_choice_dotted)
                            row.write(6, _value_)
                            row_nr += 1

                        if question.comments_allowed is True:
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(6, _comments_message_)
                            row_nr += 2
                            row = sheet.row(row_nr)
                            row.write(0, '[' + question.code + ']')
                            row.write(6, '.', style=style_dot)
                            row.write(7, None, style=style_text_unlocked)
                            for i in range(8, 17):
                                row.write(i, None, style=style_text_locked)
                            row_nr += 2
                        else:
                            row_nr += 1

                    if _type_ == 'matrix':

                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _question_)
                        row_nr += 1
                        row = sheet.row(row_nr)
                        row.write(0, '[' + question.code + ']')
                        row.write(4, _type_ + '_' + question.matrix_subtype)
                        row.hidden = isHidden
                        row_nr += 1

                        row_nr += 1
                        matrix_col_row_nr = row_nr
                        matrix_col_nr = 8
                        matrix_row_nrs = []
                        row_nr += 3

                        row_matrix_col = sheet.row(matrix_col_row_nr)
                        row_matrix_col.write(0, '[]')
                        sheet.row(matrix_col_row_nr).hidden = isHidden

                        for label in question.labels_ids_2:

                            _value_ = label.value

                            row = sheet.row(row_nr)
                            row.write(0, '[' + label.code + ']')
                            row.write(5, _value_)
                            matrix_row_nrs = matrix_row_nrs + [row_nr]
                            row_nr += 2

                        for label in question.labels_ids:

                            _value_ = label.value

                            row = sheet.row(matrix_col_row_nr)
                            row.write(matrix_col_nr, '[' + label.code + ']')
                            row = sheet.row(matrix_col_row_nr + 1)
                            row.write(matrix_col_nr + 1, _value_)
                            for matrix_row_nr in matrix_row_nrs:
                                row = sheet.row(matrix_row_nr)
                                row.write(matrix_col_nr, '.', style=style_dot)
                                row.write(matrix_col_nr + 1, None, style=style_choice_thin)
                            matrix_col_nr += 3

                        row_nr += 1

            sheet.col(0).hidden = isHidden

            if self.file_format == 'preformatted':

                for i in range(100):
                    sheet.col(i).width = 256 * 2

                sheet.protect = True
                sheet.password = self.password

            book.save(file_path)

        return True
