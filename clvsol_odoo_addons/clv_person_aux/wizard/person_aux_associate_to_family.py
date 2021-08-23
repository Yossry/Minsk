# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxAssociateToFamily(models.TransientModel):
    _description = 'Person (Aux) Associate to Family'
    _name = 'clv.person_aux.associate_to_family'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_associate_to_family_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids
    )

    # create_family = fields.Boolean(
    #     string='Create new Family',
    #     default=True,
    #     readonly=False
    # )

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

    @api.multi
    def do_person_aux_associate_to_family(self):
        self.ensure_one()

        person_aux_count = 0
        for person_aux in self.person_aux_ids:

            person_aux_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_aux_count, person_aux.name)

            Family = self.env['clv.family']
            family = False
            if person_aux.ref_address_id.id is not False:
                family = Family.search([
                    ('ref_address_id', '=', person_aux.ref_address_id.id),
                ])
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'family_id:', family.id)

            if family is not False:

                data_values = {}
                data_values['family_id'] = family.id
                _logger.info(u'>>>>>>>>>> %s', data_values)
                person_aux.write(data_values)

        # if person_aux_count == 1:

        #     action = {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Families',
        #         'res_model': 'clv.family',
        #         'res_id': family.id,
        #         'view_type': 'form',
        #         'view_mode': 'tree,kanban,form',
        #         'target': 'current',
        #         'context': {'search_default_name': family.name},
        #     }

        # else:

        #     action = {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Families',
        #         'res_model': 'clv.family',
        #         'view_type': 'form',
        #         'view_mode': 'tree,kanban,form',
        #         'target': 'current',
        #     }

        # return action
        return True
