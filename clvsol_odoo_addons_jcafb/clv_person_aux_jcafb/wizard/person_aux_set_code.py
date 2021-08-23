# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxSetCode(models.TransientModel):
    _description = 'Person (Aux) Set Code'
    _name = 'clv.person_aux.set_code'

    person_aux_ids = fields.Many2many(
        comodel_name='clv.person_aux',
        relation='clv_person_aux_set_code_rel',
        string='Persons (Aux)'
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

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        defaults['person_aux_ids'] = self.env.context['active_ids']

        return defaults

    @api.multi
    def do_person_aux_set_code(self):
        self.ensure_one()

        for person_aux in self.person_aux_ids:

            _logger.info(u'%s %s', '>>>>>', person_aux.name)

            person_aux._person_aux_set_code()

        return True
