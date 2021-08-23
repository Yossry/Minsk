# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class PersonVerificationExecute(models.TransientModel):
    _description = 'Person Verification Execute'
    _name = 'clv.person.verification_exec'

    def _default_person_ids(self):
        return self._context.get('active_ids')
    person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='clv_person_verification_outcome_refresh_rel',
        string='Persons',
        default=_default_person_ids)
    count_persons_aux = fields.Integer(
        string='Number of Persons',
        compute='_compute_count_persons_aux',
        store=False
    )

    @api.multi
    @api.depends('person_ids')
    def _compute_count_persons_aux(self):
        for r in self:
            r.count_persons_aux = len(r.person_ids)

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
    def do_person_verification_exec(self):
        self.ensure_one()

        VerificationTemplate = self.env['clv.verification.template']
        VerificationOutcome = self.env['clv.verification.outcome']

        model_name = 'clv.person'

        for person in self.person_ids:

            _logger.info(u'%s %s', '>>>>> (person):', person.name)

            verification_templates = VerificationTemplate.with_context({'active_test': False}).search([
                ('model', '=', model_name),
            ])

            for verification_template in verification_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (verification_template):', verification_template.name)

                verification_outcome = VerificationOutcome.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', person.id),
                    ('action', '=', verification_template.action),
                ])

                if verification_outcome.state is False:

                    verification_outcome_values = {}
                    verification_outcome_values['model'] = model_name
                    verification_outcome_values['res_id'] = person.id
                    verification_outcome_values['res_last_update'] = person['__last_update']
                    verification_outcome_values['state'] = 'Unknown'
                    # verification_outcome_values['method'] = verification_template.method
                    verification_outcome_values['action'] = verification_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(verification_outcome_values):', verification_outcome_values)
                    verification_outcome = VerificationOutcome.create(verification_outcome_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (verification_outcome):', verification_outcome)

                action_call = 'self.env["clv.verification.outcome"].' + \
                    verification_outcome.action + \
                    '(verification_outcome, person)'

                _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

                if action_call:

                    verification_outcome.state = 'Unknown'
                    verification_outcome.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            this_person = self.env['clv.person'].with_context({'active_test': False}).search([
                ('id', '=', person.id),
            ])
            VerificationOutcome._object_verification_outcome_model_object_verification_state_updt(this_person)

        return True
        # return self._reopen_form()
