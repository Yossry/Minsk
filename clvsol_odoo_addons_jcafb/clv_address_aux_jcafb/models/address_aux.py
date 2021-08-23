# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressAux(models.Model):
    _inherit = 'clv.address_aux'

    related_address_state = fields.Selection(
        string='Related Address State',
        related='related_address_id.state',
        store=False
    )

    @api.multi
    def do_address_aux_get_related_address_data(self):

        for address_aux in self:

            _logger.info(u'>>>>> %s', address_aux.related_address_id)

            if (address_aux.reg_state in ['draft', 'revised']) and \
               (address_aux.related_address_id.id is not False):

                data_values = {}
                # data_values['name'] = address_aux.related_address_id.name
                data_values['code'] = address_aux.related_address_id.code

                data_values['state'] = address_aux.related_address_id.state

                data_values['street'] = address_aux.related_address_id.street
                data_values['street_number'] = address_aux.related_address_id.street_number
                data_values['street2'] = address_aux.related_address_id.street2
                data_values['district'] = address_aux.related_address_id.district
                data_values['zip'] = address_aux.related_address_id.zip
                data_values['city'] = address_aux.related_address_id.city
                data_values['city_id'] = address_aux.related_address_id.city_id.id
                data_values['state_id'] = address_aux.related_address_id.state_id.id
                data_values['country_id'] = address_aux.related_address_id.country_id.id
                data_values['phone'] = address_aux.related_address_id.phone
                data_values['mobile'] = address_aux.related_address_id.mobile

                _logger.info(u'>>>>>>>>>> %s', data_values)

                address_aux.write(data_values)

        return True
