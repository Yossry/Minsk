# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PersonHistoryPersonAssociateToSet(models.TransientModel):
    _description = 'Person History Associate to Set (Person)'
    _name = 'clv.person.history.person_associate_to_set'

    def _default_person_history_ids(self):
        return self._context.get('active_ids')
    person_history_ids = fields.Many2many(
        comodel_name='clv.person.history',
        relation='clv_person_history_person_associate_to_set_rel',
        string='Person Histories',
        default=_default_person_history_ids
    )

    create_new_set = fields.Boolean(string='Create new Set', default=False)

    set_id = fields.Many2one(
        comodel_name='clv.set',
        string='Set',
        required=False
    )

    set_name = fields.Char(string='Set Name', required=False, help="Set Name")

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
    def do_person_history_person_associate_to_set(self):
        self.ensure_one()

        Set = self.env['clv.set']
        SetElement = self.env['clv.set.element']

        actual_set = False

        if self.create_new_set:

            if self.set_name is False:
                raise UserError(u'"Set Name" can not be null!')
                # return self._reopen_form()

            else:

                actual_set = Set.search([
                    ('name', '=', self.set_name),
                ])
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_set_id:', actual_set.id)

                if actual_set.id is False:

                    values = {}
                    values['name'] = self.set_name
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                    actual_set = Set.create(values)
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_set:', actual_set)

        else:

            if self.set_id.id is False:
                raise UserError(u'"Set" can not be null!')
                # return self._reopen_form()

            else:

                actual_set = self.set_id
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_set:', actual_set)

        person_count = 0
        for person_history in self.person_history_ids:

            person = person_history.person_id

            person_count += 1

            _logger.info(u'%s %s %s', '>>>>>', person_count, person.name)

            set_element = SetElement.search([
                ('set_id', '=', actual_set.id),
                ('ref_id', '=', person._name + ',' + str(person.id)),
            ])

            if set_element.id is False:

                values = {}
                values['set_id'] = actual_set.id
                values['ref_id'] = person._name + ',' + str(person.id)
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                new_set_element = SetElement.create(values)
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'new_set_element:', new_set_element)

        return True
