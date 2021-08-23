# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class VerificationOutcomeRefresh(models.TransientModel):
    _description = 'Verification Outcome Refresh'
    _name = 'clv.verification.outcome.refresh'

    def _default_outcome_ids(self):
        return self._context.get('active_ids')
    outcome_ids = fields.Many2many(
        comodel_name='clv.verification.outcome',
        relation='clv_verification_outcome_refresh_rel',
        string='Outcomes to Refresh',
        default=_default_outcome_ids)
    count_outcomes = fields.Integer(
        string='Number of Outcomes',
        compute='_compute_count_outcomes',
        store=False
    )

    @api.multi
    @api.depends('outcome_ids')
    def _compute_count_outcomes(self):
        for r in self:
            r.count_outcomes = len(r.outcome_ids)

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
    def do_verification_outcome_refresh(self):
        self.ensure_one()

        for outcome in self.outcome_ids:

            ModelObject = self.env[outcome.model]
            model_object = ModelObject.with_context({'active_test': False}).search([
                ('id', '=', outcome.res_id),
            ])

            _logger.info(u'%s %s', '>>>>>>>>>> (outcome):', outcome)

            _logger.info(u'%s %s', '>>>>>>>>>> (model_object):', model_object)

            action_call = 'self.env["clv.verification.outcome"].' + \
                outcome.action + \
                '(outcome, model_object)'

            _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

            if action_call:

                outcome.state = 'unknown'
                outcome.outcome_text = False

                exec(action_call)

        return True
        # return self._reopen_form()
