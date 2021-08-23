# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAuxAssociateToAddressAux(models.TransientModel):
    _description = 'Family (Aux) Associate to Address (Aux)'
    _name = 'clv.family_aux.associate_to_address_aux'

    def _default_family_aux_ids(self):
        return self._context.get('active_ids')
    family_aux_ids = fields.Many2many(
        comodel_name='clv.family_aux',
        relation='clv_family_aux_associate_to_address_aux_rel',
        string='Families (Aux)',
        default=_default_family_aux_ids
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
    def do_family_aux_associate_to_address_aux(self):
        self.ensure_one()

        family_aux_count = 0
        for family_aux in self.family_aux_ids:

            family_aux_count += 1

            _logger.info(u'%s %s %s', '>>>>>', family_aux_count, family_aux.name)

            AddressAux = self.env['clv.address_aux']
            address_aux = AddressAux.search([
                ('related_address_id', '=', family_aux.ref_address_id.id),
            ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>', 'address_aux_id:', address_aux.id)

            if address_aux.id is not False:

                new_address_aux = address_aux

            else:

                if self.create_new_address_aux:

                    values = {}
                    values['street'] = family_aux.ref_address_id.street

                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_address_aux = AddressAux.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_address_aux:', new_address_aux)

                    values = {}
                    values['related_address_id'] = family_aux.ref_address_id.id
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    new_address_aux.write(values)

                    new_address_aux.do_address_aux_get_related_address_data()

            data_values = {}
            data_values['ref_address_aux_id'] = new_address_aux.id
            _logger.info(u'>>>>>>>>>> %s', data_values)
            family_aux.write(data_values)

        if family_aux_count == 1:

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
