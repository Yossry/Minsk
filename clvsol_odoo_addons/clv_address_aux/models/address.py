# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Address(models.Model):
    _inherit = 'clv.address'

    address_aux_ids = fields.One2many(
        comodel_name='clv.address_aux',
        inverse_name='related_address_id',
        string='Addresses (Aux)'
    )
    count_addresses_aux = fields.Integer(
        string='Addresses (Aux) (count)',
        compute='_compute_count_addresses_aux',
        # store=True
    )

    @api.depends('address_aux_ids')
    def _compute_count_addresses_aux(self):
        for r in self:
            r.count_addresses_aux = len(r.address_aux_ids)


class AddressAux(models.Model):
    _inherit = 'clv.address_aux'

    related_address_is_unavailable = fields.Boolean(
        string='Related Address is unavailable',
        default=False,
    )
    related_address_id = fields.Many2one(comodel_name='clv.address', string='Related Address', ondelete='restrict')
    related_address_name = fields.Char(string='Related Address Name', related='related_address_id.name')
    related_address_code = fields.Char(string='Related Address Code', related='related_address_id.code')
    related_address_category_ids = fields.Many2many(
        comodel_name='clv.address.category',
        string='Related Address Categories',
        related='related_address_id.category_ids'
    )

    @api.multi
    def do_address_aux_get_related_address_data(self):

        for address_aux in self:

            _logger.info(u'>>>>> %s', address_aux.related_address_id)

            # if (address_aux.reg_state in ['draft', 'revised']) and \
            #    (address_aux.related_address_id.id is not False):
            if (address_aux.related_address_id.id is not False):

                data_values = {}
                # data_values['name'] = address_aux.related_address_id.name
                data_values['code'] = address_aux.related_address_id.code

                data_values['street'] = address_aux.related_address_id.street
                data_values['street2'] = address_aux.related_address_id.street2
                data_values['zip'] = address_aux.related_address_id.zip
                data_values['city'] = address_aux.related_address_id.city
                data_values['state_id'] = address_aux.related_address_id.state_id.id
                data_values['country_id'] = address_aux.related_address_id.country_id.id
                data_values['phone'] = address_aux.related_address_id.phone
                data_values['mobile'] = address_aux.related_address_id.mobile

                _logger.info(u'>>>>>>>>>> %s', data_values)

                address_aux.write(data_values)

        return True

    @api.multi
    def do_address_aux_remove_related_address(self):

        for address_aux in self:

            _logger.info(u'>>>>> %s', address_aux.related_address_id)

            if (address_aux.reg_state in ['draft', 'revised']) and \
               (address_aux.related_address_id.id is not False):

                data_values = {}

                if address_aux.related_address_id.id is not False:

                    data_values['related_address_id'] = False

                _logger.info(u'>>>>>>>>>> %s', data_values)

                address_aux.write(data_values)

        return True
