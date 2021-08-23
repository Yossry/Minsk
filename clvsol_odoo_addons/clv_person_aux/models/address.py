# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Address(models.Model):
    _inherit = 'clv.address'

    person_aux_ids = fields.One2many(
        comodel_name='clv.person_aux',
        inverse_name='ref_address_id',
        string='Persons (Aux)'
    )
    count_persons_aux = fields.Integer(
        string='Persons (Aux) (count)',
        compute='_compute_count_persons_aux',
        # store=True
    )

    @api.depends('person_aux_ids')
    def _compute_count_persons_aux(self):
        for r in self:
            r.count_persons_aux = len(r.person_aux_ids)


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    ref_address_is_unavailable = fields.Boolean(
        string='Address is unavailable',
        default=False,
    )
    ref_address_id = fields.Many2one(comodel_name='clv.address', string='Address', ondelete='restrict')
    ref_address_code = fields.Char(string='Address Code', related='ref_address_id.code', store=False)

    ref_address_phone = fields.Char(string='Address Phone', related='ref_address_id.phone')
    ref_address_mobile_phone = fields.Char(string='Address Mobile', related='ref_address_id.mobile')
    ref_address_email = fields.Char(string='Address Email', related='ref_address_id.email')

    ref_address_category_names = fields.Char(
        string='Address Category Names',
        related='ref_address_id.category_ids.name',
        store=True
    )
    ref_address_category_ids = fields.Many2many(
        comodel_name='clv.address.category',
        string='Address Categories',
        related='ref_address_id.category_ids'
    )

    @api.multi
    def do_person_aux_get_ref_address_data(self):

        for person_aux in self:

            _logger.info(u'>>>>> %s', person_aux.ref_address_id)

            if (person_aux.reg_state in ['draft', 'revised']) and \
               (person_aux.ref_address_id.id is not False):

                data_values = {}

                if person_aux.ref_address_id.id is not False:

                    data_values['ref_address_id'] = person_aux.ref_address_id.id

                    data_values['street'] = person_aux.ref_address_id.street
                    data_values['street2'] = person_aux.ref_address_id.street2
                    data_values['zip'] = person_aux.ref_address_id.zip
                    data_values['city'] = person_aux.ref_address_id.city
                    data_values['state_id'] = person_aux.ref_address_id.state_id.id
                    data_values['country_id'] = person_aux.ref_address_id.country_id.id
                    # data_values['phone'] = person_aux.ref_address_id.phone
                    # data_values['mobile'] = person_aux.ref_address_id.mobile

                _logger.info(u'>>>>>>>>>> %s', data_values)

                person_aux.write(data_values)

    @api.multi
    def do_person_aux_remove_ref_address(self):

        for person_aux in self:

            _logger.info(u'>>>>> %s', person_aux.ref_address_id)

            if (person_aux.reg_state in ['draft', 'revised']) and \
               (person_aux.ref_address_id.id is not False):

                data_values = {}

                if person_aux.ref_address_id.id is not False:

                    data_values['ref_address_id'] = False

                _logger.info(u'>>>>>>>>>> %s', data_values)

                person_aux.write(data_values)

        return True
