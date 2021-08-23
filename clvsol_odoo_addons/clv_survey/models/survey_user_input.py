# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    def get_value(self, question_code):

        SurveyQuestion = self.env['survey.question']
        SurveyLabel = self.env['survey.label']
        SurveyUserInput = self.env['survey.user_input_line']

        survey_question_search = SurveyQuestion.search([
            ('code', '=', question_code[:11]),
        ])
        if question_code[:11] == question_code:
            survey_user_input_line_search = SurveyUserInput.search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', survey_question_search.id),
            ])
        else:
            survey_label_search = SurveyLabel.search([
                ('code', '=', question_code),
            ])
            survey_user_input_line_search = SurveyUserInput.search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', survey_question_search.id),
                ('value_suggested_row', '=', survey_label_search.id),
            ])

        value = False

        if survey_question_search.type == 'textbox':
            value = survey_user_input_line_search.value_text

        if survey_question_search.type == 'simple_choice':
            value = ''
            if question_code[11:13] == '_C':
                for survey_user_input_line_reg in survey_user_input_line_search:
                    if survey_user_input_line_reg.value_text is not False:
                        value = survey_user_input_line_reg.value_text
            else:
                for survey_user_input_line_reg in survey_user_input_line_search:
                    if value == '':
                        value = survey_user_input_line_reg.value_suggested.value
                    else:
                        if survey_user_input_line_reg.value_suggested.value is not False:
                            value = value + '; ' + survey_user_input_line_reg.value_suggested.value
                        # else:
                        #     value = value + '; False'
                # value = survey_user_input_line_search.value_suggested.value

        if survey_question_search.type == 'multiple_choice':
            value = ''
            if question_code[11:13] == '_C':
                for survey_user_input_line_reg in survey_user_input_line_search:
                    if survey_user_input_line_reg.value_text is not False:
                        value = survey_user_input_line_reg.value_text
            else:
                for survey_user_input_line_reg in survey_user_input_line_search:
                    if value == '':
                        value = survey_user_input_line_reg.value_suggested.value
                    else:
                        if survey_user_input_line_reg.value_suggested.value is not False:
                            value = value + '; ' + survey_user_input_line_reg.value_suggested.value
                        # else:
                        #     value = value + '; False'

        if survey_question_search.type == 'matrix':
            value = ''
            for survey_user_input_line_reg in survey_user_input_line_search:
                if value == '':
                    value = survey_user_input_line_reg.value_suggested.value
                else:
                    if survey_user_input_line_reg.value_suggested.value is not False:
                        value = value + '; ' + survey_user_input_line_reg.value_suggested.value

        return value
