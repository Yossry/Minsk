# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonContactInformationUpdate(models.TransientModel):
    _description = 'Person Contact Information Update'
    _name = 'clv.person.contact_information_updt'

    def _default_person_ids(self):
        return self._context.get('active_ids')
    person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='clv_person_contact_information_updt_rel',
        string='Persons',
        default=_default_person_ids
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
    def do_person_contact_information_updt(self):
        self.ensure_one()

        person_count = 0
        for person in self.person_ids:

            person_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_count, person.name)

            if person.ref_address_id is not False:

                values = {}

                values['street'] = person.ref_address_id.street
                values['street2'] = person.ref_address_id.street2
                values['country_id'] = person.ref_address_id.country_id.id
                values['state_id'] = person.ref_address_id.state_id.id
                values['city'] = person.ref_address_id.city
                values['zip'] = person.ref_address_id.zip
                if self.updt_phone:
                    values['phone'] = person.ref_address_id.phone
                if self.updt_mobile:
                    values['mobile'] = person.ref_address_id.mobile
                if self.updt_email:
                    values['email'] = person.ref_address_id.email

                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)

                person.write(values)

        return True
