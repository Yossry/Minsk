# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Address(models.Model):
    _inherit = 'clv.address'

    family_aux_ids = fields.One2many(
        comodel_name='clv.family_aux',
        inverse_name='ref_address_id',
        string='Families (Aux)'
    )
    count_families_aux = fields.Integer(
        string='Families (Aux) (count)',
        compute='_compute_count_families_aux',
        # store=True
    )

    @api.depends('family_aux_ids')
    def _compute_count_families_aux(self):
        for r in self:
            r.count_families_aux = len(r.family_aux_ids)


class Family(models.Model):
    _inherit = 'clv.family_aux'

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
    def do_family_aux_get_ref_address_data(self):

        for family_aux in self:

            _logger.info(u'>>>>> %s', family_aux.ref_address_id)

            if (family_aux.ref_address_id.id is not False):

                data_values = {}

                if family_aux.ref_address_id.id is not False:

                    data_values['ref_address_id'] = family_aux.ref_address_id.id

                    data_values['street'] = family_aux.ref_address_id.street
                    data_values['street2'] = family_aux.ref_address_id.street2
                    data_values['zip'] = family_aux.ref_address_id.zip
                    data_values['city'] = family_aux.ref_address_id.city
                    data_values['state_id'] = family_aux.ref_address_id.state_id.id
                    data_values['country_id'] = family_aux.ref_address_id.country_id.id
                    # data_values['phone'] = family_aux.ref_address_id.phone
                    # data_values['mobile'] = family_aux.ref_address_id.mobile

                _logger.info(u'>>>>>>>>>> %s', data_values)

                family_aux.write(data_values)

        return True

    @api.multi
    def do_family_aux_remove_ref_address(self):

        for family_aux in self:

            _logger.info(u'>>>>> %s', family_aux.ref_address_id)

            if (family_aux.reg_state in ['draft', 'revised']) and \
               (family_aux.ref_address_id.id is not False):

                data_values = {}

                if family_aux.ref_address_id.id is not False:

                    data_values['ref_address_id'] = False

                _logger.info(u'>>>>>>>>>> %s', data_values)

                family_aux.write(data_values)

        return True
