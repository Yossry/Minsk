# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Family(models.Model):
    _inherit = 'clv.family'

    person_ids = fields.One2many(
        comodel_name='clv.person',
        inverse_name='family_id',
        string='Persons'
    )
    count_persons = fields.Integer(
        string='Persons (count)',
        compute='_compute_count_persons',
        # store=True
    )

    # @api.depends('person_ids')
    def _compute_count_persons(self):
        for r in self:
            r.count_persons = len(r.person_ids)


class Person(models.Model):
    _inherit = 'clv.person'

    family_is_unavailable = fields.Boolean(
        string='Family is unavailable',
        default=False,
    )
    family_id = fields.Many2one(comodel_name='clv.family', string='Family', ondelete='restrict')
    family_code = fields.Char(string='Family Code', related='family_id.code', store=False)

    family_category_ids = fields.Char(
        string='Family Categories',
        related='family_id.category_ids.name',
        store=True
    )

    @api.multi
    def do_person_associate_to_family_with_reference_address(self):

        for person in self:

            _logger.info(u'>>>>> %s', person.ref_address_id)

            Family = self.env['clv.family']

            if (person.ref_address_id.id is not False):

                data_values = {}

                family = Family.search([
                    ('ref_address_id', '=', person.ref_address_id.id),
                ])

                if family.id is not False:

                    data_values['family_id'] = family.id

                _logger.info(u'>>>>>>>>>> %s', data_values)

                person.write(data_values)

        return True
