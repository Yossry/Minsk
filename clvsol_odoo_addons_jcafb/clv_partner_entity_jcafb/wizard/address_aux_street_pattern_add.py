# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AddressAuxStreetPatternAdd(models.TransientModel):
    _description = 'Address (Aux) Street Pattern Add'
    _name = 'clv.address_aux.street_pattern_add'

    def _default_address_aux_ids(self):
        return self._context.get('active_ids')
    address_aux_ids = fields.Many2many(
        comodel_name='clv.address_aux',
        relation='clv_address_aux_street_pattern_add_rel',
        string='Addresses (Aux)',
        default=_default_address_aux_ids)
    count_addresses_aux = fields.Integer(
        string='Number of Addresses (Aux)',
        compute='_compute_count_addresses_aux',
        store=False
    )

    @api.multi
    @api.depends('address_aux_ids')
    def _compute_count_addresses_aux(self):
        for r in self:
            r.count_addresses_aux = len(r.address_aux_ids)

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
    def do_address_aux_street_pattern_add(self):
        self.ensure_one()

        PartnerEntityStreetPattern = self.env['clv.partner_entity.street_pattern']

        for address_aux in self.address_aux_ids:

            _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (address_aux):', address_aux.name)

            street_patern = PartnerEntityStreetPattern.search([
                ('street', '=', address_aux.street),
                ('district', '=', address_aux.district),
            ])

            if street_patern.street is False:

                values = {}
                values['street'] = address_aux.street
                values['district'] = address_aux.district
                values['active'] = True
                PartnerEntityStreetPattern.create(values)

        return True
