# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAssociateToPersonAux(models.TransientModel):
    _description = 'Person Associate to Person (Aux)'
    _name = 'clv.person.associate_to_person_aux'

    def _default_person_ids(self):
        return self._context.get('active_ids')
    person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='clv_person_associate_to_person_aux_rel',
        string='Persons',
        default=_default_person_ids
    )

    create_new_person_aux = fields.Boolean(
        string='Create new Person (Aux)',
        default=True,
        readonly=False
    )

    create_new_address_aux = fields.Boolean(
        string='Create new Address (Aux)',
        default=False,
        readonly=False
    )

    create_new_family_aux = fields.Boolean(
        string='Create new Family (Aux)',
        default=False,
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
    def do_person_associate_to_person_aux(self):
        self.ensure_one()

        person_count = 0
        for person in self.person_ids:

            person_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_count, person.name)

            PersonAux = self.env['clv.person_aux']
            person_aux = PersonAux.search([
                ('related_person_id', '=', person.id),
            ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'person_aux_id:', person_aux.id)

            if person_aux.id is not False:

                new_person_aux = person_aux

            else:

                if self.create_new_person_aux:

                    values = {}
                    values['name'] = person.name

                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_person_aux = PersonAux.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_person_aux:', new_person_aux)

                    values = {}
                    values['related_person_id'] = person.id
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_person_aux.write(values)

                    new_person_aux.do_person_aux_get_related_person_data()

            if person.ref_address_id.id is not False:

                new_address_aux = False

                AddressAux = self.env['clv.address_aux']
                address_aux = AddressAux.search([
                    ('related_address_id', '=', person.ref_address_id.id),
                ])
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'address_aux_id:', address_aux.id)

                if address_aux.id is not False:

                    new_address_aux = address_aux

                else:

                    if self.create_new_address_aux:

                        values = {}
                        values['street'] = new_person_aux.ref_address_id.street

                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                        new_address_aux = AddressAux.create(values)
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_address_aux:', new_address_aux)

                        values = {}
                        values['related_address_id'] = new_person_aux.ref_address_id.id
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                        new_address_aux.write(values)

                        new_address_aux.do_address_aux_get_related_address_data()

                if new_address_aux is not False:

                    data_values = {}
                    data_values['ref_address_aux_id'] = new_address_aux.id
                    _logger.info(u'>>>>>>>>>> %s', data_values)
                    new_person_aux.write(data_values)

            if person.family_id.id is not False:

                new_family_aux = False

                FamilyAux = self.env['clv.family_aux']
                family_aux = FamilyAux.search([
                    ('related_family_id', '=', person.family_id.id),
                ])
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'family_aux_id:', family_aux.id)

                if family_aux.id is not False:

                    new_family_aux = family_aux

                else:

                    if self.create_new_family_aux:

                        values = {}
                        values['street'] = new_person_aux.family_id.street

                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                        new_family_aux = FamilyAux.create(values)
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_family_aux:', new_family_aux)

                        values = {}
                        values['related_family_id'] = new_person_aux.family_id.id
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                        new_family_aux.write(values)

                        new_family_aux.do_family_aux_get_related_family_data()

                if new_family_aux is not False:

                    data_values = {}
                    data_values['family_aux_id'] = new_family_aux.id
                    _logger.info(u'>>>>>>>>>> %s', data_values)
                    new_person_aux.write(data_values)

                    AddressAux = self.env['clv.address_aux']
                    address_aux = AddressAux.search([
                        ('related_address_id', '=', new_family_aux.ref_address_id.id),
                    ])
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'address_aux_id:', address_aux.id)

                    if address_aux.id is not False:

                        new_address_aux = address_aux

                    else:

                        if self.create_new_address_aux:

                            values = {}
                            values['street'] = new_family_aux.ref_address_id.street

                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                            new_address_aux = AddressAux.create(values)
                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_address_aux:', new_address_aux)

                            values = {}
                            values['related_address_id'] = new_family_aux.ref_address_id.id
                            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                            new_address_aux.write(values)

                            new_address_aux.do_address_aux_get_related_address_data()

                    if new_address_aux is not False:

                        data_values = {}
                        data_values['ref_address_aux_id'] = new_address_aux.id
                        _logger.info(u'>>>>>>>>>> %s', data_values)
                        new_family_aux.write(data_values)

        if person_count == 1:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Persons (Aux)',
                'res_model': 'clv.person_aux',
                'res_id': new_person_aux.id,
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
                'context': {'search_default_name': new_person_aux.name},
            }

        else:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Persons (Aux)',
                'res_model': 'clv.person_aux',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }

        return action
        # return True
