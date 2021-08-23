# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxContactInformationUpdate(models.TransientModel):
    _description = 'Person (Aux) Contact Information Update'
    _name = 'clv.person_aux.contact_information_updt'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_contact_information_updt_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids
    )

    updt_phone = fields.Boolean(string='Update Phone', default=False)
    updt_mobile = fields.Boolean(string='Update Mobile', default=False)
    updt_email = fields.Boolean(string='Update Email', default=False)

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
    def do_person_aux_contact_information_updt(self):
        self.ensure_one()

        for person_aux in self.person_aux_ids:

            _logger.info(u'%s %s', '>>>>>', person_aux.name)

            if person_aux.ref_address_id is not False:

                person_aux.street = person_aux.ref_address_id.street
                person_aux.street2 = person_aux.ref_address_id.street2
                person_aux.country_id = person_aux.ref_address_id.country_id
                person_aux.state_id = person_aux.ref_address_id.state_id
                person_aux.city = person_aux.ref_address_id.city
                person_aux.zip = person_aux.ref_address_id.zip
                if self.updt_phone:
                    person_aux.phone = person_aux.ref_address_id.phone
                if self.updt_mobile:
                    person_aux.mobile = person_aux.ref_address_id.mobile
                if self.updt_email:
                    person_aux.email = person_aux.ref_address_id.email

        return True
