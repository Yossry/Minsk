# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SurveyUserInputValidate(models.TransientModel):
    _description = 'Survey User Input Validate'
    _name = 'survey.user_input.validate'

    def _default_survey_user_input_ids(self):
        return self._context.get('active_ids')
    survey_user_input_ids = fields.Many2many(
        comodel_name='survey.user_input',
        relation='survey_user_input_validate_rel',
        string='Survey User Inputs',
        default=_default_survey_user_input_ids
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
    def do_survey_user_input_validate(self):
        self.ensure_one()

        for survey_user_input in self.survey_user_input_ids:

            _logger.info(u'%s %s', '>>>>>', survey_user_input.token)

            if survey_user_input.state in ['new', 'skip']:

                survey_user_input.state_2 = 'returned'
                if survey_user_input.notes is False:
                    survey_user_input.notes = \
                        u'Erro: A Entrada de Respostas ainda não foi concluída!'
                else:
                    survey_user_input.notes += \
                        u'\nErro: A Entrada de Respostas ainda não foi concluída!'

            elif survey_user_input.state_2 in ['checked', 'validated']:

                if survey_user_input.document_id.survey_user_input_id.id is not False:

                    if survey_user_input.document_id.survey_user_input_id.id != survey_user_input.id:

                        survey_user_input.state_2 = 'returned'
                        if survey_user_input.notes is False:
                            survey_user_input.notes = \
                                u'Erro: O Documento já está associado a outra Entrada de Respostas!'
                        else:
                            survey_user_input.notes += \
                                u'\nErro: O Documento já está associado a outra Entrada de Respostas!'

                    else:

                        survey_user_input.state_2 = 'validated'

                else:

                    survey_user_input.document_id.survey_user_input_id = survey_user_input.id
                    survey_user_input.state_2 = 'validated'

        return True

    @api.multi
    def do_populate_all_survey_user_inputs(self):
        self.ensure_one()

        SurveyUserInput = self.env['survey.user_input']
        survey_user_inputs = SurveyUserInput.search([])

        self.survey_user_input_ids = survey_user_inputs

        return self._reopen_form()
