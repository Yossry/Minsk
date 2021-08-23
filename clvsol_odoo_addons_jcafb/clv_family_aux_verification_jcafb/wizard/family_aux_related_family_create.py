# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAuxRelateFamilyCreate(models.TransientModel):
    _description = 'Family (Aux) Related Family Create'
    _name = 'clv.family_aux.related_family_create'

    family_aux_ids = fields.Many2many(
        comodel_name='clv.family_aux',
        relation='clv_family_aux_related_family_create_rel',
        string='Families (Aux)'
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
    def do_family_aux_related_family_create(self):
        self.ensure_one()

        Family = self.env['clv.family']

        for family_aux in self.family_aux_ids:

            _logger.info(u'%s %s', '>>>>>', family_aux.name)

            if not family_aux.related_family_is_unavailable:

                if family_aux.related_family_id.id is False:

                    family = Family.search([
                        ('name', '=', family_aux.name),
                    ])

                    if family.id is False:

                        vals = {}

                        if (family_aux.code is not False):

                            vals['code'] = family_aux.code

                        if (family_aux.phase_id.id is not False):

                            vals['phase_id'] = family_aux.phase_id.id

                        if (family_aux.state is not False):

                            vals['state'] = family_aux.state

                        if (family_aux.name is not False):

                            vals['name'] = family_aux.name

                        if (family_aux.zip is not False):

                            vals['zip'] = family_aux.zip

                        if (family_aux.street is not False):

                            vals['street'] = family_aux.street

                        if (family_aux.street_number is not False):

                            vals['street_number'] = family_aux.street_number

                        if (family_aux.street2 is not False):

                            vals['street2'] = family_aux.street2

                        if (family_aux.district is not False):

                            vals['district'] = family_aux.district

                        if (family_aux.country_id.id is not False):

                            vals['country_id'] = family_aux.country_id.id

                        if (family_aux.state_id.id is not False):

                            vals['state_id'] = family_aux.state_id.id

                        if (family_aux.city_id.id is not False):

                            vals['city_id'] = family_aux.city_id.id

                        if (family_aux.phone is not False):

                            vals['phone'] = family_aux.phone

                        if (family_aux.mobile is not False):

                            vals['mobile'] = family_aux.mobile

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

                        if (family_aux.ref_address_is_unavailable is not False):

                            vals['ref_address_is_unavailable'] = family_aux.ref_address_is_unavailable

                        if (family_aux.ref_address_id.id is not False):

                            vals['ref_address_id'] = family_aux.ref_address_id.id

                        if vals != {}:

                            vals['reg_state'] = 'revised'

                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'vals:', vals)
                            new_related_family = Family.create(vals)

                            values = {}
                            values['related_family_id'] = new_related_family.id
                            family_aux.write(values)

                    else:

                        values = {}
                        values['related_family_id'] = family.id
                        family_aux.write(values)

        return True
