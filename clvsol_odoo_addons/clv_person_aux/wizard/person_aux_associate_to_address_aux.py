# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxAssociateToAddressAux(models.TransientModel):
    _description = 'Person (Aux) Associate to Address (Aux)'
    _name = 'clv.person_aux.associate_to_address_aux'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_associate_to_address_aux_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids
    )

    create_new_address_aux = fields.Boolean(
        string='Create new Address (Aux)',
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
    def do_person_aux_associate_to_address_aux(self):
        self.ensure_one()

        person_aux_count = 0
        for person_aux in self.person_aux_ids:

            person_aux_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_aux_count, person_aux.name)

            AddressAux = self.env['clv.address_aux']
            address_aux = AddressAux.search([
                ('related_address_id', '=', person_aux.ref_address_id.id),
            ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'address_aux_id:', address_aux.id)

            new_address_aux = False

            if address_aux.id is not False:

                new_address_aux = address_aux

            else:

                if self.create_new_address_aux:

                    values = {}
                    values['street'] = person_aux.ref_address_id.street

                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_address_aux = AddressAux.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_address_aux:', new_address_aux)

                    values = {}
                    values['related_address_id'] = person_aux.ref_address_id.id
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_address_aux.write(values)

                    new_address_aux.do_address_aux_get_related_address_data()

            if new_address_aux is not False:

                data_values = {}
                data_values['ref_address_aux_id'] = new_address_aux.id
                _logger.info(u'>>>>>>>>>> %s', data_values)
                person_aux.write(data_values)
                person_aux.do_person_aux_get_ref_address_aux_data()

        if person_aux_count == 1:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Addresses (Aux)',
                'res_model': 'clv.address_aux',
                'res_id': new_address_aux.id,
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
                'context': {'search_default_name': new_address_aux.name},
            }

        else:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Addresses (Aux)',
                'res_model': 'clv.address_aux',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }

        return action
        # return True
