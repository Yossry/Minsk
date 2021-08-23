# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxAssociateToRelatedPersonFamily(models.TransientModel):
    _description = 'Person (Aux) Associate to Related Person Family'
    _name = 'clv.person_aux.associate_to_related_person_family'

    def _default_person_aux_ids(self):
        return self._context.get('active_ids')
    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_associate_to_related_person_family_rel',
        string='Persons (Aux)',
        default=_default_person_aux_ids
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
    def do_person_aux_associate_to_related_person_family(self):
        self.ensure_one()

        person_aux_count = 0
        for person_aux in self.person_aux_ids:

            person_aux_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_aux_count, person_aux.name)

            family = False
            if person_aux.related_person_id.id is not False:
                if person_aux.related_person_id.family_id.id is not False:
                    family = person_aux.related_person_id.family_id

            if family is not False:

                data_values = {}
                data_values['family_id'] = family.id
                _logger.info(u'>>>>>>>>>> %s', data_values)
                person_aux.write(data_values)

        # return action
        return True
