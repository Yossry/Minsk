# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
import base64



class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_attachment = fields.Binary('Question attachment')
    type = fields.Selection([
        ('free_text', 'Multiple Lines Text Box'),
        ('textbox', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('date', 'Date'),
        ('upload_file', 'Upload file'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix')], string='Type of Question', default='free_text', required=True)


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    answer_type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('free_text', 'Free Text'),
        ('upload_file', 'Upload file'),
        ('suggestion', 'Suggestion'),
        ('list', 'List box'),
        ('matrix_models', 'Matrix models')], string='Answer Type')

    file = fields.Binary('Upload file')
    file_type = fields.Selection([('image', 'image'), ('pdf', 'pdf')])

    @api.model
    def save_line_upload_file(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        file_name = str(post[answer_tag])
        file_type = file_name.find("('application/pdf')")
        image_type = file_name.find("('image/png')")
        if file_type > -1:
            vals.update({'file_type': 'pdf'})
        if image_type > -1:
            vals.update({'file_type': 'image'})

        if question.constr_mandatory:
            file = base64.encodebytes(post[answer_tag].read())
        else:
            file = base64.encodebytes(post[answer_tag].read()) if post[answer_tag] else None
        if answer_tag in post:
            vals.update({'answer_type': 'upload_file', 'file': file})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True

