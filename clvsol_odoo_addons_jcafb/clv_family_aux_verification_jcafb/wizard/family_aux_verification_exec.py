# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class FamilyAuxVerificationExecute(models.TransientModel):
    _description = 'Family (Aux) Verification Execute'
    _name = 'clv.family_aux.verification_exec'

    def _default_family_aux_ids(self):
        return self._context.get('active_ids')
    family_aux_ids = fields.Many2many(
        comodel_name='clv.family_aux',
        relation='clv_family_aux_verification_outcome_refresh_rel',
        string='Families (Aux)',
        default=_default_family_aux_ids)
    count_families_aux = fields.Integer(
        string='Number of Families (Aux)',
        compute='_compute_count_families_aux',
        store=False
    )

    @api.multi
    @api.depends('family_aux_ids')
    def _compute_count_families_aux(self):
        for r in self:
            r.count_families_aux = len(r.family_aux_ids)

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
    def do_family_aux_verification_exec(self):
        self.ensure_one()

        for family_aux in self.family_aux_ids:

            family_aux.family_aux_verification_exec()

        return True
