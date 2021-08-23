# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from functools import reduce

from odoo import models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractProcess(models.AbstractModel):
    _inherit = 'clv.abstract.process'

    def _do_survey_user_input_copy(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>> schedule:', schedule.name)

        from time import time
        start = time()

        SurveyUserInput = self.env['survey.user_input']
        SurveyUserInputLine = self.env['survey.user_input_line']

        # external_host = 'https://clvheatlh-jcafb-2020-aws-tst.tklapp.com'
        # external_dbname = 'clvhealth_jcafb_2020'
        # external_user = 'admin'
        external_host = schedule.external_host_id.name
        external_dbname = schedule.external_host_id.external_dbname
        external_user = schedule.external_host_id.external_user
        external_user_pw = schedule.external_host_id.external_user_pw

        uid, sock, login_msg = self.external_host_login(
            external_host,
            external_dbname,
            external_user,
            external_user_pw
        )

        if uid is not False:

            model = 'survey.user_input'
            args = []
            fields = ['id', 'token']

            user_inputs = sock.execute(external_dbname, uid, external_user_pw,
                                       model,
                                       'search_read',
                                       args,
                                       fields)

            count_user_inputs = 0
            count_user_input_lines = 0
            count_user_input_lines_total = 0

            for user_input in user_inputs:

                count_user_inputs += 1

                _logger.info(u'>>>>>>>>>>>> %s %s', count_user_inputs, user_input)

                model = 'survey.user_input'
                args = [('id', '=', user_input['id'])]
                fields = ['date_create', 'token', 'survey_id', 'deadline', 'type',
                          'state', 'test_entry', 'partner_id', 'email', 'last_displayed_page_id']

                user_input_data = sock.execute(external_dbname, uid, external_user_pw,
                                               model,
                                               'search_read',
                                               args,
                                               fields)
                user_input_data = user_input_data[0]

                _logger.info(u'>>>>>>>>>>>> %s', user_input_data)

                date_create = user_input_data['date_create']
                token = user_input_data['token']
                survey_id = False
                if user_input_data['survey_id'] is not False:
                    survey_id = user_input_data['survey_id'][0]
                deadline = user_input_data['deadline']
                type = user_input_data['type']
                state = user_input_data['state']
                test_entry = user_input_data['test_entry']
                partner_id = False
                if user_input_data['partner_id'] is not False:
                    partner_id = user_input_data['partner_id'][0]
                email = user_input_data['email']
                last_displayed_page_id = False
                if user_input_data['last_displayed_page_id'] is not False:
                    last_displayed_page_id = user_input_data['last_displayed_page_id'][0]

                values = {}
                values['date_create'] = date_create
                values['token'] = token
                values['survey_id'] = survey_id
                values['deadline'] = deadline
                values['type'] = type
                values['state'] = state
                values['test_entry'] = test_entry
                values['partner_id'] = partner_id
                values['email'] = email
                values['last_displayed_page_id'] = last_displayed_page_id

                new_survey_user_input = SurveyUserInput.create(values)

                model = 'survey.user_input_line'
                args = [('user_input_id', '=', user_input['id'])]
                fields = ['id']

                user_input_lines = sock.execute(external_dbname, uid, external_user_pw,
                                                model,
                                                'search_read',
                                                args,
                                                fields)

                count_user_input_lines = 0
                for user_input_line in user_input_lines:

                    count_user_input_lines += 1
                    count_user_input_lines_total += 1

                    _logger.info(u'>>>>>>>>>>>>>>>> %s (%s) %s',
                                 count_user_input_lines, count_user_input_lines_total, user_input_line)

                    model = 'survey.user_input_line'
                    args = [('id', '=', user_input_line['id'])]
                    fields = ['date_create', 'user_input_id', 'question_id', 'survey_id', 'skipped',
                              'answer_type', 'value_text', 'value_number', 'value_date', 'value_free_text',
                              'value_suggested', 'value_suggested_row', 'quizz_mark']

                    user_input_line_data = sock.execute(external_dbname, uid, external_user_pw,
                                                        model,
                                                        'search_read',
                                                        args,
                                                        fields)
                    user_input_line_data = user_input_line_data[0]

                    _logger.info(u'>>>>>>>>>>>>>>>>> %s', user_input_line_data)

                    date_create = user_input_line_data['date_create']
                    user_input_id = new_survey_user_input.id
                    question_id = False
                    if user_input_line_data['question_id'] is not False:
                        question_id = user_input_line_data['question_id'][0]
                    survey_id = False
                    if user_input_line_data['survey_id'] is not False:
                        survey_id = user_input_line_data['survey_id'][0]
                    skipped = user_input_line_data['skipped']
                    answer_type = user_input_line_data['answer_type']
                    value_text = user_input_line_data['value_text']
                    value_number = user_input_line_data['value_number']
                    value_date = user_input_line_data['value_date']
                    value_free_text = user_input_line_data['value_free_text']
                    value_suggested = False
                    if user_input_line_data['value_suggested'] is not False:
                        value_suggested = user_input_line_data['value_suggested'][0]
                    value_suggested_row = False
                    if user_input_line_data['value_suggested_row'] is not False:
                        value_suggested_row = user_input_line_data['value_suggested_row'][0]
                    quizz_mark = user_input_line_data['quizz_mark']

                    values = {}
                    values['date_create'] = date_create
                    values['user_input_id'] = user_input_id
                    values['question_id'] = question_id
                    values['survey_id'] = survey_id
                    values['skipped'] = skipped
                    values['answer_type'] = answer_type
                    values['value_text'] = value_text
                    values['value_number'] = value_number
                    values['value_date'] = value_date
                    values['value_free_text'] = value_free_text
                    values['value_suggested'] = value_suggested
                    values['value_suggested_row'] = value_suggested_row
                    values['quizz_mark'] = quizz_mark

                    SurveyUserInputLine.create(values)

            _logger.info(u'%s %s', '>>>>>>>> count_user_inputs: ', count_user_inputs)
            _logger.info(u'%s %s', '>>>>>>>> count_user_input_lines_total: ', count_user_input_lines_total)
            _logger.info(u'%s %s', '>>>>>>>> Execution time: ', secondsToStr(time() - start))
