# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAuxRelateFamilyUpdt(models.TransientModel):
    _description = 'Family (Aux) Related Family Update'
    _name = 'clv.family_aux.related_family_updt'

    family_aux_ids = fields.Many2many(
        comodel_name='clv.family_aux',
        relation='clv_family_aux_related_family_updt_rel',
        string='Families (Aux)'
    )

    update_contact_info_data = fields.Boolean(
        string='Update Contact Information Data',
        default=True,
        readonly=False
    )

    update_ref_address_data = fields.Boolean(
        string='Update Address Data',
        default=False,
        readonly=False
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

        defaults['family_aux_ids'] = self.env.context['active_ids']

        return defaults

    @api.multi
    def do_family_aux_related_family_updt(self):
        self.ensure_one()

        for family_aux in self.family_aux_ids:

            _logger.info(u'%s %s', '>>>>>', family_aux.name)

            if not family_aux.related_family_is_unavailable:

                related_family = family_aux.related_family_id
                vals = {}

                if (family_aux.phase_id != related_family.phase_id):

                    vals['phase_id'] = family_aux.phase_id.id

                if (family_aux.state != related_family.state):

                    vals['state'] = family_aux.state

                if (family_aux.global_tag_ids.id is not False):

                    m2m_list = []
                    count = 0
                    for global_tag_id in family_aux.global_tag_ids:
                        m2m_list.append((4, global_tag_id.id))
                        count += 1

                    if count > 0:
                        vals['global_tag_ids'] = m2m_list

                if (family_aux.category_ids.id is not False):

                    m2m_list = []
                    count = 0
                    for global_tag_id in family_aux.category_ids:
                        m2m_list.append((4, global_tag_id.id))
                        count += 1

                    if count > 0:
                        vals['category_ids'] = m2m_list

                if (family_aux.marker_ids.id is not False):

                    m2m_list = []
                    count = 0
                    for global_tag_id in family_aux.marker_ids:
                        m2m_list.append((4, global_tag_id.id))
                        count += 1

                    if count > 0:
                        vals['marker_ids'] = m2m_list

                if (family_aux.name != related_family.name):

                    vals['name'] = family_aux.name

                if self.update_contact_info_data:

                    if (family_aux.contact_info_is_unavailable != related_family.contact_info_is_unavailable):

                        vals['contact_info_is_unavailable'] = family_aux.contact_info_is_unavailable

                    if (family_aux.zip != related_family.zip):

                        vals['zip'] = family_aux.zip

                    if (family_aux.street != related_family.street):

                        vals['street'] = family_aux.street

                    if (family_aux.street_number != related_family.street_number):

                        vals['street_number'] = family_aux.street_number

                    if (family_aux.street2 != related_family.street2):

                        vals['street2'] = family_aux.street2

                    if (family_aux.district != related_family.district):

                        vals['district'] = family_aux.district

                    if (family_aux.country_id != related_family.country_id):

                        vals['country_id'] = family_aux.country_id.id

                    if (family_aux.state_id != related_family.state_id):

                        vals['state_id'] = family_aux.state_id.id

                    if (family_aux.city_id != related_family.city_id):

                        vals['city_id'] = family_aux.city_id.id

                    if (family_aux.phone is not False) and (family_aux.phone != related_family.phone):

                        vals['phone'] = family_aux.phone

                    if (family_aux.mobile is not False) and (family_aux.mobile != related_family.mobile):

                        vals['mobile'] = family_aux.mobile

                if self.update_ref_address_data:

                    if (family_aux.ref_address_is_unavailable != related_family.ref_address_is_unavailable):

                        vals['ref_address_is_unavailable'] = family_aux.ref_address_is_unavailable

                    if (family_aux.ref_address_id != related_family.ref_address_id):

                        vals['ref_address_id'] = family_aux.ref_address_id.id

                if vals != {}:

                    vals['reg_state'] = 'revised'

                _logger.info(u'%s %s', '>>>>>>>>>>', vals)
                related_family.write(vals)

        return True
