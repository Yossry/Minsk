# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class FamilyVerificationExecute(models.TransientModel):
    _description = 'Family Verification Execute'
    _name = 'clv.family.verification_exec'

    def _default_family_ids(self):
        return self._context.get('active_ids')
    family_ids = fields.Many2many(
        comodel_name='clv.family',
        relation='clv_family_verification_outcome_refresh_rel',
        string='Families',
        default=_default_family_ids)
    count_families = fields.Integer(
        string='Number of Families',
        compute='_compute_count_families',
        store=False
    )

    @api.multi
    @api.depends('family_ids')
    def _compute_count_families(self):
        for r in self:
            r.count_families = len(r.family_ids)

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
    def do_family_verification_exec(self):
        self.ensure_one()

        for family in self.family_ids:

            family.family_verification_exec()

        return True
