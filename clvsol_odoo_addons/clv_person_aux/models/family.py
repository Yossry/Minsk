# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Family(models.Model):
    _inherit = 'clv.family'

    person_aux_ids = fields.One2many(
        comodel_name='clv.person_aux',
        inverse_name='family_id',
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
    def do_person_aux_remove_family(self):

        for person_aux in self:

            _logger.info(u'>>>>> %s', person_aux.family_id)

            if (person_aux.reg_state in ['draft', 'revised']) and \
               (person_aux.family_id.id is not False):

                data_values = {}

                if person_aux.family_id.id is not False:

                    data_values['family_id'] = False

                _logger.info(u'>>>>>>>>>> %s', data_values)

                person_aux.write(data_values)

        return True
