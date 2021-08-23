# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Address(models.Model):
    _inherit = 'clv.address'

    family_ids = fields.One2many(
        comodel_name='clv.family',
        inverse_name='ref_address_id',
        string='Families'
    )
    count_families = fields.Integer(
        string='Families (count)',
        compute='_compute_count_families',
        # store=True
    )

    # @api.depends('family_ids')
    def _compute_count_families(self):
        for r in self:
            r.count_families = len(r.family_ids)


class Family(models.Model):
    _inherit = 'clv.family'

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
    def do_family_get_ref_address_data(self):

        for family in self:

            _logger.info(u'>>>>> %s', family.ref_address_id)

            if (family.ref_address_id.id is not False):

                data_values = {}

                if family.ref_address_id.id is not False:

                    data_values['ref_address_id'] = family.ref_address_id.id

                    data_values['street'] = family.ref_address_id.street
                    data_values['street2'] = family.ref_address_id.street2
                    data_values['zip'] = family.ref_address_id.zip
                    data_values['city'] = family.ref_address_id.city
                    data_values['state_id'] = family.ref_address_id.state_id.id
                    data_values['country_id'] = family.ref_address_id.country_id.id
                    # data_values['phone'] = family.ref_address_id.phone
                    # data_values['mobile'] = family.ref_address_id.mobile

                _logger.info(u'>>>>>>>>>> %s', data_values)

                family.write(data_values)

        return True
