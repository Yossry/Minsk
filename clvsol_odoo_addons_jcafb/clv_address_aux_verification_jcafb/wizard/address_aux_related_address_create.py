# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressAuxRelateAddressCreate(models.TransientModel):
    _description = 'Address (Aux) Related Address Create'
    _name = 'clv.address_aux.related_address_create'

    address_aux_ids = fields.Many2many(
        comodel_name='clv.address_aux',
        relation='clv_address_aux_related_address_create_rel',
        string='Addresses (Aux)'
    )

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

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        defaults['address_aux_ids'] = self.env.context['active_ids']

        return defaults

    @api.multi
    def do_address_aux_related_address_create(self):
        self.ensure_one()

        Address = self.env['clv.address']

        for address_aux in self.address_aux_ids:

            _logger.info(u'%s %s', '>>>>>', address_aux.name)

            if not address_aux.related_address_is_unavailable:

                if address_aux.related_address_id.id is False:

                    address = Address.search([
                        ('street', '=', address_aux.street),
                        ('street_number', '=', address_aux.street_number),
                        ('street2', '=', address_aux.street2),
                        ('district', '=', address_aux.district),
                    ])

                    if address.id is False:

                        vals = {}

                        if (address_aux.code is not False):

                            vals['code'] = address_aux.code

                        if (address_aux.phase_id.id is not False):

                            vals['phase_id'] = address_aux.phase_id.id

                        if (address_aux.state is not False):

                            vals['state'] = address_aux.state

                        if (address_aux.zip is not False):

                            vals['zip'] = address_aux.zip

                        if (address_aux.street is not False):

                            vals['street'] = address_aux.street

                        if (address_aux.street_number is not False):

                            vals['street_number'] = address_aux.street_number

                        if (address_aux.street2 is not False):

                            vals['street2'] = address_aux.street2

                        if (address_aux.district is not False):

                            vals['district'] = address_aux.district

                        if (address_aux.country_id.id is not False):

                            vals['country_id'] = address_aux.country_id.id

                        if (address_aux.state_id.id is not False):

                            vals['state_id'] = address_aux.state_id.id

                        if (address_aux.city_id.id is not False):

                            vals['city_id'] = address_aux.city_id.id

                        if (address_aux.phone is not False):

                            vals['phone'] = address_aux.phone

                        if (address_aux.mobile is not False):

                            vals['mobile'] = address_aux.mobile

                        if (address_aux.global_tag_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in address_aux.global_tag_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['global_tag_ids'] = m2m_list

                        if (address_aux.category_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in address_aux.category_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['category_ids'] = m2m_list

                        if (address_aux.marker_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in address_aux.marker_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['marker_ids'] = m2m_list

                        if vals != {}:

                            vals['reg_state'] = 'revised'

                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'vals:', vals)
                            new_related_address = Address.create(vals)

                            values = {}
                            values['related_address_id'] = new_related_address.id
                            address_aux.write(values)

                    else:

                        values = {}
                        values['related_address_id'] = address.id
                        address_aux.write(values)

        return True
