# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SurveyDuplicate(models.TransientModel):
    _description = 'Survey Duplicate'
    _name = 'survey.survey.duplicate'

    survey_ids = fields.Many2many(
        comodel_name='survey.survey',
        relation='survey_survey_duplicate_rel',
        string='Lab Test Types'
    )

    new_title = fields.Char(
        string='New Survey Title',
        required=True
    )

    new_description = fields.Char(
        string='New Survey Description',
        required=True
    )

    new_code = fields.Char(
        string='New Survey Code',
        required=True
    )

    @api.model
    def default_get(self, field_names):

        defaults = super(SurveyDuplicate, self).default_get(field_names)

        defaults['survey_ids'] = self.env.context['active_ids']

        Survey = self.env['survey.survey']
        survey_id = self._context.get('active_id')
        survey = Survey.search([
            ('id', '=', survey_id),
        ])
        defaults['new_title'] = survey.title
        defaults['new_description'] = survey.description
        defaults['new_code'] = survey.code

        return defaults

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
    def do_survey_duplicate(self):
        self.ensure_one()

        SurveySurvey = self.env['survey.survey']
        SurveyPage = self.env['survey.page']
        SurveyQuestion = self.env['survey.question']
        SurveyLabel = self.env['survey.label']

        for survey in self.survey_ids:

            _logger.info(u'%s %s %s %s', '>>>>>', survey.code, survey.title, survey.description)
            _logger.info(u'%s %s %s %s', '>>>>>>>>>>', self.new_code, self.new_title, self.new_description)

            values = {
                'title': self.new_title,
                'code': self.new_code,
                'stage_id': survey.stage_id.id,
                'auth_required': survey.auth_required,
                'users_can_go_back': survey.users_can_go_back,
                'description': self.new_description,
                'thank_you_message': survey.thank_you_message,
            }
            new_survey = SurveySurvey.create(values)

            for page in survey.page_ids:

                new_page_code = page.code.replace(survey.code, self.new_code)

                _logger.info(u'%s %s %s', '>>>>>>>>>>>>>>>', new_page_code, page.title)

                values = {
                    'title': page.title,
                    'code': new_page_code,
                    'survey_id': new_survey.id,
                    'sequence': page.sequence,
                    'description': page.description,
                }
                new_page = SurveyPage.create(values)

                for question in page.question_ids:

                    new_question_code = question.code.replace(survey.code, self.new_code)

                    _logger.info(u'%s %s %s', '>>>>>>>>>>>>>>>>>>>>', new_question_code, question.question)

                    values = {
                        'question': question.question,
                        'code': new_question_code,
                        'parameter': question.parameter,
                        'type': question.type,
                        'page_id': new_page.id,
                        'sequence': question.sequence,
                        'constr_mandatory': question.constr_mandatory,
                        'constr_error_msg': question.constr_error_msg,

                        'display_mode': question.display_mode,
                        'column_nb': question.column_nb,
                        'comments_allowed': question.comments_allowed,
                        'comments_message': question.comments_message,

                        'matrix_subtype': question.matrix_subtype,
                    }
                    new_question = SurveyQuestion.create(values)

                    for label in question.labels_ids:

                        new_label_code = label.code.replace(survey.code, self.new_code)

                        _logger.info(u'%s %s %s', '>>>>>>>>>>>>>>>>>>>>>>>>>', new_label_code, label.value)

                        values = {
                            'value': label.value,
                            'code': new_label_code,
                            'question_id': new_question.id,
                            'sequence': label.sequence,
                        }
                        SurveyLabel.create(values)

                    for label in question.labels_ids_2:

                        new_label_code = label.code.replace(survey.code, self.new_code)

                        _logger.info(u'%s %s %s', '>>>>>>>>>>>>>>>>>>>>>>>>>', new_label_code, label.value)

                        values = {
                            'value': label.value,
                            'code': new_label_code,
                            'question_id_2': new_question.id,
                            'sequence': label.sequence,
                        }
                        SurveyLabel.create(values)

        return True
