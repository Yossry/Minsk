# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SurveyCodeRenew(models.TransientModel):
    _description = 'Survey Code Renew'
    _name = 'clv.survey.code_renew'

    def _default_survey_ids(self):
        return self._context.get('active_ids')
    survey_ids = fields.Many2many(
        comodel_name='survey.survey',
        relation='clv_survey_code_renew_rel',
        string='Surveys',
        default=_default_survey_ids
    )

    @api.multi
    def do_survey_code_renew(self):
        self.ensure_one()

        for survey in self.survey_ids:

            _logger.info(u'%s %s', '>>>>>', survey.title)
            _logger.info(u'%s %s', '>>>>>', survey.code)

            new_survey_code = 'x' + survey.code

            new_page_sequence = 0
            for page in survey.page_ids:

                new_page_sequence += 10
                if new_page_sequence < 100:
                    new_page_code = new_survey_code + '_0' + str(int(new_page_sequence / 10))
                else:
                    new_page_code = new_survey_code + '_' + str(int(new_page_sequence / 10))

                _logger.info(
                    u'%s %s: %s, %s: %s',
                    '>>>>>>>>>>', page.code, page.sequence, new_page_code[1:], new_page_sequence
                )

                new_question_sequence = 0
                for question in page.question_ids:

                    _type_ = question.type

                    new_question_sequence += 10
                    if new_question_sequence < 100:
                        new_question_code = new_page_code + '_0' + str(int(new_question_sequence / 10))
                    else:
                        new_question_code = new_page_code + '_' + str(int(new_question_sequence / 10))

                    _logger.info(
                        u'%s %s: %s, %s: %s',
                        '>>>>>>>>>>>>>>>',
                        question.code, question.sequence, new_question_code[1:], new_question_sequence
                    )

                    if _type_ == 'free_text' or _type_ == 'textbox' or _type_ == 'datetime':

                        pass

                    if _type_ == 'simple_choice':

                        new_label_sequence = 0
                        for label in question.labels_ids:

                            new_label_sequence += 10
                            if new_label_sequence < 100:
                                new_label_code = new_question_code + '_0' + str(int(new_label_sequence / 10))
                            else:
                                new_label_code = new_question_code + '_' + str(int(new_label_sequence / 10))

                            _logger.info(
                                u'%s %s: %s, %s: %s',
                                '>>>>>>>>>>>>>>>>>>>>',
                                label.code, label.sequence, new_label_code[1:], new_label_sequence
                            )

                            label.sequence = new_label_sequence
                            label.code = new_label_code

                    if _type_ == 'multiple_choice':

                        new_label_sequence = 0
                        for label in question.labels_ids:

                            new_label_sequence += 10
                            if new_label_sequence < 100:
                                new_label_code = new_question_code + '_0' + str(int(new_label_sequence / 10))
                            else:
                                new_label_code = new_question_code + '_' + str(int(new_label_sequence / 10))

                            _logger.info(
                                u'%s %s: %s, %s: %s',
                                '>>>>>>>>>>>>>>>>>>>>',
                                label.code, label.sequence, new_label_code[1:], new_label_sequence
                            )

                            label.sequence = new_label_sequence
                            label.code = new_label_code

                    if _type_ == 'matrix':

                        new_label_sequence = 0
                        for label in question.labels_ids_2:

                            new_label_sequence += 10
                            if new_label_sequence < 100:
                                new_label_code = new_question_code + '_0' + str(int(new_label_sequence / 10))
                            else:
                                new_label_code = new_question_code + '_' + str(int(new_label_sequence / 10))

                            _logger.info(
                                u'%s %s: %s, %s: %s',
                                '>>>>>>>>>>>>>>>>>>>>',
                                label.code, label.sequence, new_label_code[1:], new_label_sequence
                            )

                            label.sequence = new_label_sequence
                            label.code = new_label_code

                        for label in question.labels_ids:

                            new_label_sequence += 10
                            if new_label_sequence < 100:
                                new_label_code = new_question_code + '_0' + str(int(new_label_sequence / 10))
                            else:
                                new_label_code = new_question_code + '_' + str(int(new_label_sequence / 10))

                            _logger.info(
                                u'%s %s: %s, %s: %s',
                                '>>>>>>>>>>>>>>>>>>>>',
                                label.code, label.sequence, new_label_code[1:], new_label_sequence
                            )

                            label.sequence = new_label_sequence
                            label.code = new_label_code

                    question.sequence = new_question_sequence
                    question.code = new_question_code

                page.sequence = new_page_sequence
                page.code = new_page_code

            for page in survey.page_ids:
                page.code = page.code[1:]
                for question in page.question_ids:
                    question.code = question.code[1:]
                    for label in question.labels_ids_2:
                        label.code = label.code[1:]
                    for label in question.labels_ids:
                        label.code = label.code[1:]

        return True
