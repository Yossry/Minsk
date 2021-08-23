# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AddressStreetPatternAdd(models.TransientModel):
    _description = 'Address Street Pattern Add'
    _name = 'clv.address.street_pattern_add'

    def _default_address_ids(self):
        return self._context.get('active_ids')
    address_ids = fields.Many2many(
        comodel_name='clv.address',
        relation='clv_address_street_pattern_add_rel',
        string='Addresses',
        default=_default_address_ids)
    count_addresses = fields.Integer(
        string='Number of Addresses',
        compute='_compute_count_addresses',
        store=False
    )

    @api.multi
    @api.depends('address_ids')
    def _compute_count_addresses(self):
        for r in self:
            r.count_addresses = len(r.address_ids)

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
    def do_address_street_pattern_add(self):
        self.ensure_one()

        PartnerEntityStreetPattern = self.env['clv.partner_entity.street_pattern']

        for address in self.address_ids:

            _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (address):', address.name)

            street_patern = PartnerEntityStreetPattern.search([
                ('street', '=', address.street),
                ('district', '=', address.district),
            ])

            if street_patern.street is False:

                values = {}
                values['street'] = address.street
                values['district'] = address.district
                values['active'] = True
                PartnerEntityStreetPattern.create(values)

        return True
