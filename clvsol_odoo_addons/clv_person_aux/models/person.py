# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Person(models.Model):
    _inherit = 'clv.person'

    person_aux_ids = fields.One2many(
        comodel_name='clv.person_aux',
        inverse_name='related_person_id',
        string='Persons (Aux)'
    )
    count_person_auxs = fields.Integer(
        string='Persons (Aux) (count)',
        compute='_compute_count_person_auxs',
        # store=True
    )

    @api.depends('person_aux_ids')
    def _compute_count_person_auxs(self):
        for r in self:
            r.count_person_auxs = len(r.person_aux_ids)


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    related_person_is_unavailable = fields.Boolean(
        string='Related Person is unavailable',
        default=False,
    )
    related_address_id = fields.Many2one(comodel_name='clv.address', string='Related Address', ondelete='restrict')
    related_person_id = fields.Many2one(comodel_name='clv.person', string='Related Person', ondelete='restrict')
    related_person_name = fields.Char(string='Related Person Name', related='related_person_id.name')
    related_person_code = fields.Char(string='Related Person Code', related='related_person_id.code')
    related_person_category_ids = fields.Many2many(
        comodel_name='clv.person.category',
        string='Related Person Categories',
        related='related_person_id.category_ids'
    )
    related_person_ref_address_id = fields.Many2one(
        comodel_name='clv.address',
        string='Related Person Address',
        related='related_person_id.ref_address_id'
    )
    related_person_ref_address_code = fields.Char(
        string='Related Person Address Code',
        related='related_person_id.ref_address_id.code'
    )
    related_person_ref_address_category_ids = fields.Many2many(
        comodel_name='clv.address.category',
        string='Related Person Address Categories',
        related='related_person_id.ref_address_id.category_ids'
    )

    @api.multi
    def do_person_aux_get_related_person_data(self):

        for person_aux in self:

            _logger.info(u'>>>>> %s', person_aux.related_person_id)

            if (person_aux.reg_state in ['draft', 'revised']) and \
               (person_aux.related_person_id.id is not False):

                data_values = {}
                data_values['name'] = person_aux.related_person_id.name
                data_values['code'] = person_aux.related_person_id.code
                data_values['gender'] = person_aux.related_person_id.gender
                data_values['birthday'] = person_aux.related_person_id.birthday
                data_values['responsible_id'] = person_aux.related_person_id.responsible_id.id
                data_values['caregiver_id'] = person_aux.related_person_id.caregiver_id.id

                if self.related_person_id.ref_address_id.id is not False:

                    data_values['ref_address_id'] = person_aux.related_person_id.ref_address_id.id

                    data_values['street'] = person_aux.related_person_id.ref_address_id.street
                    data_values['street2'] = person_aux.related_person_id.ref_address_id.street2
                    data_values['zip'] = person_aux.related_person_id.ref_address_id.zip
                    data_values['city'] = person_aux.related_person_id.ref_address_id.city
                    data_values['state_id'] = person_aux.related_person_id.ref_address_id.state_id.id
                    data_values['country_id'] = person_aux.related_person_id.ref_address_id.country_id.id
                    # data_values['phone'] = person_aux.related_person_id.ref_address_id.phone
                    # data_values['mobile'] = person_aux.related_person_id.ref_address_id.mobile

                if person_aux.related_person_id.family_id.id is not False:

                    data_values['family_id'] = person_aux.related_person_id.family_id.id

                _logger.info(u'>>>>>>>>>> %s', data_values)

                person_aux.write(data_values)

        return True
