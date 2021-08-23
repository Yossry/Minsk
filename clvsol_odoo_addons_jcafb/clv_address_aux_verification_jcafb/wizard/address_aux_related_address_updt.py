# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressAuxRelateAddressUpdt(models.TransientModel):
    _description = 'Address (Aux) Related Address Update'
    _name = 'clv.address_aux.related_address_updt'

    address_aux_ids = fields.Many2many(
        comodel_name='clv.address_aux',
        relation='clv_address_aux_related_address_updt_rel',
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
    def do_address_aux_related_address_updt(self):
        self.ensure_one()

        for address_aux in self.address_aux_ids:

            _logger.info(u'%s %s', '>>>>>', address_aux.name)

            if not address_aux.related_address_is_unavailable:

                related_address = address_aux.related_address_id
                vals = {}

                if (address_aux.phase_id != related_address.phase_id):

                    vals['phase_id'] = address_aux.phase_id.id

                if (address_aux.state != related_address.state):

                    vals['state'] = address_aux.state

                if (address_aux.zip != related_address.zip):

                    vals['zip'] = address_aux.zip

                if (address_aux.street != related_address.street):

                    vals['street'] = address_aux.street

                if (address_aux.street_number != related_address.street_number):

                    vals['street_number'] = address_aux.street_number

                if (address_aux.street2 != related_address.street2):

                    vals['street2'] = address_aux.street2

                if (address_aux.district != related_address.district):

                    vals['district'] = address_aux.district

                if (address_aux.country_id != related_address.country_id):

                    vals['country_id'] = address_aux.country_id.id

                if (address_aux.state_id != related_address.state_id):

                    vals['state_id'] = address_aux.state_id.id

                if (address_aux.city_id != related_address.city_id):

                    vals['city_id'] = address_aux.city_id.id

                if (address_aux.phone is not False) and (address_aux.phone != related_address.phone):

                    vals['phone'] = address_aux.phone

                if (address_aux.mobile is not False) and (address_aux.mobile != related_address.mobile):

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

                if (address_aux.code != related_address.code):

                    vals['code'] = address_aux.code

                if vals != {}:

                    vals['reg_state'] = 'revised'

                _logger.info(u'%s %s', '>>>>>>>>>>', vals)
                related_address.write(vals)

        return True
