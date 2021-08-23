# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxAssociateToFamilyAux(models.TransientModel):
    _description = 'Person (Aux) Associate to Family (Aux)'
    _name = 'clv.person_aux.associate_to_family_aux'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_associate_to_family_aux_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids
    )

    create_new_family_aux = fields.Boolean(
        string='Create new Family (Aux)',
        default=True,
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

    @api.multi
    def do_person_aux_associate_to_family_aux(self):
        self.ensure_one()

        person_aux_count = 0
        for person_aux in self.person_aux_ids:

            person_aux_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_aux_count, person_aux.name)

            FamilyAux = self.env['clv.family_aux']
            family_aux = False
            if person_aux.family_id.id is not False:
                family_aux = FamilyAux.search([
                    ('related_family_id', '=', person_aux.family_id.id),
                ])
            elif person_aux.ref_address_aux_id.id is not False:
                family_aux = FamilyAux.search([
                    ('ref_address_aux_id', '=', person_aux.ref_address_aux_id.id),
                ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'family_aux_id:', family_aux.id)

            new_family_aux = False

            if family_aux.id is not False:

                new_family_aux = family_aux

            else:

                if self.create_new_family_aux:

                    values = {}
                    values['street'] = person_aux.family_id.street

                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_family_aux = FamilyAux.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_family_aux:', new_family_aux)

                    values = {}
                    values['related_family_id'] = person_aux.family_id.id
                    values['ref_address_id'] = person_aux.ref_address_id.id
                    values['ref_address_aux_id'] = person_aux.ref_address_aux_id.id
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_family_aux.write(values)

                    # new_family_aux.do_family_aux_get_related_family_data()
                    new_family_aux.do_family_aux_get_ref_address_aux_data()

            if new_family_aux is not False:

                data_values = {}
                data_values['family_aux_id'] = new_family_aux.id
                _logger.info(u'>>>>>>>>>> %s', data_values)
                person_aux.write(data_values)

        if person_aux_count == 1:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Families (Aux)',
                'res_model': 'clv.family_aux',
                'res_id': new_family_aux.id,
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
                'context': {'search_default_name': new_family_aux.name},
            }

        else:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Families (Aux)',
                'res_model': 'clv.family_aux',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }

        return action
        # return True
