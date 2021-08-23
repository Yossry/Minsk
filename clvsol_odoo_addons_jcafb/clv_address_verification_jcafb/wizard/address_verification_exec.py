# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AddressVerificationExecute(models.TransientModel):
    _description = 'Address Verification Execute'
    _name = 'clv.address.verification_exec'

    def _default_address_ids(self):
        return self._context.get('active_ids')
    address_ids = fields.Many2many(
        comodel_name='clv.address',
        relation='clv_address_verification_outcome_refresh_rel',
        string='Addresses',
        default=_default_address_ids)
    count_addresses_aux = fields.Integer(
        string='Number of Addresses',
        compute='_compute_count_addresses_aux',
        store=False
    )

    @api.multi
    @api.depends('address_ids')
    def _compute_count_addresses_aux(self):
        for r in self:
            r.count_addresses_aux = len(r.address_ids)

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
    def do_address_verification_exec(self):
        self.ensure_one()

        for address in self.address_ids:

            address.address_verification_exec()

        return True
