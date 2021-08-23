# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class PersonAuxVerificationExecute(models.TransientModel):
    _description = 'Person (Aux) Verification Execute'
    _name = 'clv.person_aux.verification_exec'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_verification_outcome_refresh_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids)
    count_persons_aux = fields.Integer(
        string='Number of Persons (Aux)',
        compute='_compute_count_persons_aux',
        store=False
    )

    @api.multi
    @api.depends('person_aux_ids')
    def _compute_count_persons_aux(self):
        for r in self:
            r.count_persons_aux = len(r.person_aux_ids)

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
    def do_person_aux_verification_exec(self):
        self.ensure_one()

        for person_aux in self.person_aux_ids:

            person_aux.person_aux_verification_exec()

        return True
