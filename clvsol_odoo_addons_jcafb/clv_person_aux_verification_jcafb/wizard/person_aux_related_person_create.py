# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxRelatePersonCreate(models.TransientModel):
    _description = 'Person (Aux) Related Person Create'
    _name = 'clv.person_aux.related_person_create'

    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_related_person_create_rel',
        string='Persons (Aux)'
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

        defaults['person_aux_ids'] = self.env.context['active_ids']

        return defaults

    @api.multi
    def do_person_aux_related_person_create(self):
        self.ensure_one()

        Person = self.env['clv.person']

        for person_aux in self.person_aux_ids:

            _logger.info(u'%s %s', '>>>>>', person_aux.name)

            if not person_aux.related_person_is_unavailable:

                if person_aux.related_person_id.id is False:

                    person = Person.search([
                        ('name', '=', person_aux.name),
                    ])

                    if person.id is False:

                        vals = {}

                        if (person_aux.code is not False):

                            vals['code'] = person_aux.code

                        if (person_aux.phase_id.id is not False):

                            vals['phase_id'] = person_aux.phase_id.id

                        if (person_aux.state is not False):

                            vals['state'] = person_aux.state

                        if (person_aux.name is not False):

                            vals['name'] = person_aux.name

                        if (person_aux.is_absent is not False):

                            vals['is_absent'] = person_aux.is_absent

                        if (person_aux.gender is not False):

                            vals['gender'] = person_aux.gender

                        if (person_aux.birthday is not False):

                            vals['birthday'] = person_aux.birthday

                        if (person_aux.date_death is not False):

                            vals['date_death'] = person_aux.date_death

                        if (person_aux.force_is_deceased is not False):

                            vals['force_is_deceased'] = person_aux.force_is_deceased

                        if (person_aux.zip is not False):

                            vals['zip'] = person_aux.zip

                        if (person_aux.street is not False):

                            vals['street'] = person_aux.street

                        if (person_aux.street_number is not False):

                            vals['street_number'] = person_aux.street_number

                        if (person_aux.street2 is not False):

                            vals['street2'] = person_aux.street2

                        if (person_aux.district is not False):

                            vals['district'] = person_aux.district

                        if (person_aux.country_id.id is not False):

                            vals['country_id'] = person_aux.country_id.id

                        if (person_aux.state_id.id is not False):

                            vals['state_id'] = person_aux.state_id.id

                        if (person_aux.city_id.id is not False):

                            vals['city_id'] = person_aux.city_id.id

                        if (person_aux.phone is not False):

                            vals['phone'] = person_aux.phone

                        if (person_aux.mobile is not False):

                            vals['mobile'] = person_aux.mobile

                        if (person_aux.global_tag_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in person_aux.global_tag_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['global_tag_ids'] = m2m_list

                        if (person_aux.category_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in person_aux.category_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['category_ids'] = m2m_list

                        if (person_aux.marker_ids.id is not False):

                            m2m_list = []
                            count = 0
                            for global_tag_id in person_aux.marker_ids:
                                m2m_list.append((4, global_tag_id.id))
                                count += 1

                            if count > 0:
                                vals['marker_ids'] = m2m_list

                        if (person_aux.ref_address_is_unavailable is not False):

                            vals['ref_address_is_unavailable'] = person_aux.ref_address_is_unavailable

                        if (person_aux.ref_address_id.id is not False):

                            vals['ref_address_id'] = person_aux.ref_address_id.id

                        if (person_aux.family_is_unavailable is not False):

                            vals['family_is_unavailable'] = person_aux.family_is_unavailable

                        if (person_aux.family_id.id is not False):

                            vals['family_id'] = person_aux.family_id.id

                        if vals != {}:

                            vals['reg_state'] = 'revised'

                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'vals:', vals)
                            new_related_person = Person.create(vals)

                            values = {}
                            values['related_person_id'] = new_related_person.id
                            person_aux.write(values)

                    else:

                        values = {}
                        values['related_person_id'] = person.id
                        person_aux.write(values)

        return True
