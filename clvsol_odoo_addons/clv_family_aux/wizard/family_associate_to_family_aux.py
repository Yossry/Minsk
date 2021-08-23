# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAssociateToFamilyAux(models.TransientModel):
    _description = 'Family Associate to Family (Aux)'
    _name = 'clv.family.associate_to_family_aux'

    def _default_family_ids(self):
        return self._context.get('active_ids')
    family_ids = fields.Many2many(
        comodel_name='clv.family',
        relation='clv_family_associate_to_family_aux_rel',
        string='Families',
        default=_default_family_ids
    )

    create_new_family_aux = fields.Boolean(
        string='Create new Family (Aux)',
        default=True,
        readonly=False
    )

    create_new_address_aux = fields.Boolean(
        string='Create new Address (Aux)',
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
    def do_family_associate_to_family_aux(self):
        self.ensure_one()

        family_count = 0
        for family in self.family_ids:

            family_count += 1

            _logger.info(u'%s %s %s', '>>>>>', family_count, family.name)

            FamilyAux = self.env['clv.family_aux']
            family_aux = FamilyAux.search([
                ('related_family_id', '=', family.id),
            ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'family_aux_id:', family_aux.id)

            if family_aux.id is not False:

                new_family_aux = family_aux

            else:

                if self.create_new_family_aux:

                    values = {}
                    values['street'] = family.street

                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_family_aux = FamilyAux.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_family_aux:', new_family_aux)

                    values = {}
                    values['related_family_id'] = family.id
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_family_aux.write(values)

                    new_family_aux.do_family_aux_get_related_family_data()

            if family.ref_address_id.id is not False:

                new_address_aux = False

                AddressAux = self.env['clv.address_aux']
                address_aux = AddressAux.search([
                    ('related_address_id', '=', family.ref_address_id.id),
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

        if family_count == 1:

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
