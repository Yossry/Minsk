# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SurveyExportXML(models.TransientModel):
    _description = 'Survey Export XML'
    _name = 'clv.survey.export_xml'

    def _default_survey_ids(self):
        return self._context.get('active_ids')
    survey_ids = fields.Many2many(
        comodel_name='survey.survey',
        relation='clv_survey_export_xml_rel',
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
        'Directory Path',
        required=True,
        help="Directory Path",
        default=_default_dir_path
    )

    file_name = fields.Char(
        'File Name',
        required=True,
        help="File Name",
        default='survey_jcafb_<code>.xml'
    )

    @api.multi
    def do_survey_export_xml(self):
        self.ensure_one()

        for survey_reg in self.survey_ids:

            file_path = self.dir_path + '/' + self.file_name.replace('<code>', survey_reg.code)

            _logger.info(u'%s %s', '>>>>>', file_path)

            xml_file = open(file_path, "w")

            xml_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            xml_file.write('<odoo>\n')
            xml_file.write('    <data noupdate="1">\n')
            xml_file.write('\n')

            _model_ = 'survey.survey'
            _stage_id_ = 'survey.stage_in_progress'
            _description_ = survey_reg.description.replace('<p>', '').replace('</p>', '')
            _thank_you_message_ = survey_reg.thank_you_message.replace('<p>', '').replace('</p>', '')

            xml_file.write('        <!-- %s -->\n' % (survey_reg.title))
            xml_file.write('        <record model="%s" id="%s">\n' % (_model_, survey_reg.code))
            xml_file.write('            <field name="title">%s</field>\n' % (survey_reg.title))
            xml_file.write('            <field name="code">%s</field>\n' % (survey_reg.code))
            xml_file.write('            <field name="stage_id" ref="%s"/>\n' % (_stage_id_))
            xml_file.write('            <field name="auth_required" eval="%s"/>\n' % (survey_reg.auth_required))
            xml_file.write('            <field name="users_can_go_back" eval="%s"/>\n' %
                           (survey_reg.users_can_go_back))
            xml_file.write('            <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' % (_description_))
            xml_file.write('            <field name="thank_you_message">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                           (_thank_you_message_))
            xml_file.write('        </record>\n')
            xml_file.write('\n')

            for page in survey_reg.page_ids:

                _title_ = page.title
                _model_ = 'survey.page'
                _description_ = page.description.replace('<p>', '').replace('</p>', '')

                xml_file.write('            <!-- %s -->\n' % (_title_))
                xml_file.write('            <record model="%s" id="%s">\n' % (_model_, page.code))
                xml_file.write('                <field name="title">%s</field>\n' % (_title_))
                xml_file.write('                <field name="code">%s</field>\n' % (page.code))
                xml_file.write('                <field name="survey_id" ref="%s"/>\n' % (survey_reg.code))
                xml_file.write('                <field name="sequence" eval="%s"/>\n' % (page.sequence))
                xml_file.write('                <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                               (_description_))
                xml_file.write('            </record>' + '\n')
                xml_file.write('\n')

                for question in page.question_ids:

                    _type_ = question.type
                    _question_ = question.question
                    _model_ = 'survey.question'
                    if question.comments_message is not False:
                        _comments_message_ = question.comments_message
                    if question.comments_allowed is False:
                        _comments_message_ = ''

                    if _type_ == 'free_text' or _type_ == 'textbox' or _type_ == 'datetime':

                        xml_file.write('                <!-- %s -->\n' % (_question_))
                        xml_file.write('                <record model="%s" id="%s">\n' % (_model_, question.code))
                        xml_file.write('                    <field name="question">%s</field>\n' % (_question_))
                        xml_file.write('                    <field name="code">%s</field>\n' % (question.code))
                        if question.parameter:
                            xml_file.write('                    <field name="parameter">%s</field>\n' %
                                           (question.parameter))
                        xml_file.write('                    <field name="type">%s</field>\n' % (_type_))
                        xml_file.write('                    <field name="page_id" ref="%s"/>\n' % (page.code))
                        xml_file.write('                    <field name="sequence" eval="%s"/>\n' %
                                       (question.sequence))
                        xml_file.write('                    <field name="constr_mandatory">%s</field>\n' %
                                       (question.constr_mandatory))
                        xml_file.write('                    <field name="constr_error_msg">%s</field>\n' %
                                       (question.constr_error_msg))
                        xml_file.write('                </record>\n')
                        xml_file.write('\n')

                    if _type_ == 'simple_choice':

                        xml_file.write('                <!-- %s -->\n' % (_question_))
                        xml_file.write('                <record model="%s" id="%s">\n' % (_model_, question.code))
                        xml_file.write('                    <field name="question">%s</field>\n' % (_question_))
                        xml_file.write('                    <field name="code">%s</field>\n' % (question.code))
                        if question.parameter:
                            xml_file.write('                    <field name="parameter">%s</field>\n' %
                                           (question.parameter))
                        xml_file.write('                    <field name="type">%s</field>\n' % (_type_))
                        xml_file.write('                    <field name="page_id" ref="%s"/>\n' % (page.code))
                        xml_file.write('                    <field name="sequence" eval="%s"/>\n' %
                                       (question.sequence))
                        xml_file.write('                    <field name="display_mode">%s</field>\n' %
                                       (question.display_mode))
                        xml_file.write('                    <field name="column_nb">%s</field>\n' %
                                       (question.column_nb))
                        xml_file.write('                    <field name="constr_mandatory">%s</field>\n' %
                                       (question.constr_mandatory))
                        xml_file.write('                    <field name="constr_error_msg">%s</field>\n' %
                                       (question.constr_error_msg))
                        xml_file.write('                    <field name="comments_allowed">%s</field>\n' %
                                       (question.comments_allowed))
                        xml_file.write('                    <field name="comments_message">%s</field>\n' %
                                       (_comments_message_))
                        xml_file.write('                </record>\n')
                        xml_file.write('\n')

                        for label in question.labels_ids:

                            _model_ = 'survey.label'

                            xml_file.write('                    <record model="%s" id="%s">\n' % (_model_, label.code))
                            xml_file.write('                        <field name="value">%s</field>\n' %
                                           (label.value))
                            xml_file.write('                        <field name="code">%s</field>\n' % (label.code))
                            xml_file.write('                        <field name="question_id" ref="%s"/>\n' %
                                           (question.code))
                            xml_file.write('                        <field name="sequence" eval="%s"/>\n' %
                                           (label.sequence))
                            xml_file.write('                    </record>\n')
                            xml_file.write('\n')

                    if _type_ == 'multiple_choice':

                        xml_file.write('                <!-- %s -->\n' % (_question_))
                        xml_file.write('                <record model="%s" id="%s">\n' % (_model_, question.code))
                        xml_file.write('                    <field name="question">%s</field>\n' % (_question_))
                        xml_file.write('                    <field name="code">%s</field>\n' % (question.code))
                        if question.parameter:
                            xml_file.write('                    <field name="parameter">%s</field>\n' %
                                           (question.parameter))
                        xml_file.write('                    <field name="type">%s</field>\n' % (_type_))
                        xml_file.write('                    <field name="page_id" ref="%s"/>\n' % (page.code))
                        xml_file.write('                    <field name="sequence" eval="%s"/>\n' %
                                       (question.sequence))
                        xml_file.write('                    <field name="column_nb">%s</field>\n' %
                                       (question.column_nb))
                        xml_file.write('                    <field name="constr_mandatory">%s</field>\n' %
                                       (question.constr_mandatory))
                        xml_file.write('                    <field name="constr_error_msg">%s</field>\n' %
                                       (question.constr_error_msg))
                        xml_file.write('                    <field name="comments_allowed">%s</field>\n' %
                                       (question.comments_allowed))
                        xml_file.write('                    <field name="comments_message">%s</field>\n' %
                                       (_comments_message_))
                        xml_file.write('                </record>\n')
                        xml_file.write('\n')

                        for label in question.labels_ids:

                            _model_ = 'survey.label'

                            xml_file.write('                    <record model="%s" id="%s">\n' % (_model_, label.code))
                            xml_file.write('                        <field name="value">%s</field>\n' %
                                           (label.value))
                            xml_file.write('                        <field name="code">%s</field>\n' % (label.code))
                            xml_file.write('                        <field name="question_id" ref="%s"/>\n' %
                                           (question.code))
                            xml_file.write('                        <field name="sequence" eval="%s"/>\n' %
                                           (label.sequence))
                            xml_file.write('                    </record>\n')
                            xml_file.write('\n')

                    if _type_ == 'matrix':

                        xml_file.write('                <!-- %s -->\n' % (_question_))
                        xml_file.write('                <record model="%s" id="%s">\n' % (_model_, question.code))
                        xml_file.write('                    <field name="question">%s</field>\n' % (_question_))
                        xml_file.write('                    <field name="code">%s</field>\n' % (question.code))
                        if question.parameter:
                            xml_file.write('                    <field name="parameter">%s</field>\n' %
                                           (question.parameter))
                        xml_file.write('                    <field name="type">%s</field>\n' % (_type_))
                        xml_file.write('                    <field name="matrix_subtype">%s</field>\n' %
                                       (question.matrix_subtype))
                        xml_file.write('                    <field name="page_id" ref="%s"/>\n' % (page.code))
                        xml_file.write('                    <field name="sequence" eval="%s"/>\n' %
                                       (question.sequence))
                        xml_file.write('                    <field name="constr_mandatory">%s</field>\n' %
                                       (question.constr_mandatory))
                        xml_file.write('                    <field name="constr_error_msg">%s</field>\n' %
                                       (question.constr_error_msg))
                        xml_file.write('                </record>\n')
                        xml_file.write('\n')

                        for label in question.labels_ids_2:

                            _model_ = 'survey.label'

                            xml_file.write('                    <record model="%s" id="%s">\n' % (_model_, label.code))
                            xml_file.write('                        <field name="value">%s</field>\n' %
                                           (label.value))
                            xml_file.write('                        <field name="code">%s</field>\n' % (label.code))
                            xml_file.write('                        <field name="question_id_2" ref="%s"/>\n' %
                                           (question.code))
                            xml_file.write('                        <field name="sequence" eval="%s"/>\n' %
                                           (label.sequence))
                            xml_file.write('                    </record>\n')
                            xml_file.write('\n')

                        for label in question.labels_ids:

                            _model_ = 'survey.label'

                            xml_file.write('                    <record model="%s" id="%s">\n' % (_model_, label.code))
                            xml_file.write('                        <field name="value">%s</field>\n' %
                                           (label.value))
                            xml_file.write('                        <field name="code">%s</field>\n' % (label.code))
                            xml_file.write('                        <field name="question_id" ref="%s"/>\n' %
                                           (question.code))
                            xml_file.write('                        <field name="sequence" eval="%s"/>\n' %
                                           (label.sequence))
                            xml_file.write('                    </record>\n')
                            xml_file.write('\n')

            xml_file.write('    </data>\n')
            xml_file.write('</odoo>\n')

            xml_file.close()

        return True
