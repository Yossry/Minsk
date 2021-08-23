# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo import exceptions

_logger = logging.getLogger(__name__)


class PersonHistoryUpdate(models.TransientModel):
    _description = 'Person History Update'
    _name = 'clv.person.history_updt'

    def _default_person_ids(self):
        return self._context.get('active_ids')
    person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='person_history_updt_rel',
        string='Persons',
        default=_default_person_ids
    )
    date_sign_in = fields.Date(
        string='Sign in date',
        required=False,
    )
    date_sign_out = fields.Date(
        string="Sign out date",
        required=False
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
    def do_person_history_updt(self):
        self.ensure_one()

        PersonHistory = self.env['clv.person.history']

        for person in self.person_ids:

            if self.date_sign_out is False:
                raise exceptions.ValidationError('The "Sign out date" has not been defined!')
                return self._reopen_form()

            if self.date_sign_in is False:
                raise exceptions.ValidationError('The "Sign in date" has not been defined!')
                return self._reopen_form()

            _logger.info(u'%s %s', '>>>>>', person.name)

            if person.phase_id.id is not False:

                person_history = PersonHistory.search([
                    ('person_id', '=', person.id),
                    ('phase_id', '=', person.phase_id.id),
                    ('date_sign_out', '=', False),
                ])

                if person_history.id is False:

                    person_history_2 = PersonHistory.search([
                        ('person_id', '=', person.id),
                        ('date_sign_out', '=', False),
                    ])
                    if person_history_2.id is not False:
                        person_history_2.date_sign_out = self.date_sign_out
                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>', person_history_2.phase_id.name,
                                                     person_history_2.date_sign_in,
                                                     person_history_2.date_sign_out)

                    m2m_list = []
                    for category_id in person.category_ids:
                        m2m_list.append((4, category_id.id))
                    category_ids = m2m_list
                    m2m_list = []
                    for marker_id in person.marker_ids:
                        m2m_list.append((4, marker_id.id))
                    marker_ids = m2m_list
                    values = {
                        'phase_id': person.phase_id.id,
                        'date_sign_in': self.date_sign_in,
                        'state': person.state,
                        'reg_state': person.reg_state,
                        'employee_id': person.employee_id.id,
                        'person_id': person.id,
                        'category_ids': category_ids,
                        'marker_ids': marker_ids,
                        'responsible_id': person.responsible_id.id,
                        'caregiver_id': person.caregiver_id.id,
                        'ref_family_id': person.family_id.id,
                        'ref_address_id': person.ref_address_id.id,
                    }
                    person_history = PersonHistory.create(values)
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', person_history.phase_id.name,
                                                 person_history.date_sign_in,
                                                 person_history.date_sign_out)

                else:

                    if person_history.state != person.state:
                        person_history.state = person.state

                    if person_history.reg_state != person.reg_state:
                        person_history.reg_state = person.reg_state

                    if person_history.employee_id.id != person.employee_id.id:
                        person_history.employee_id = person.employee_id.id

                    m2m_list = []
                    for category_id in person.category_ids:
                        m2m_list.append((4, category_id.id))
                    m2m_list_2 = []
                    for category_id in person_history.category_ids:
                        m2m_list_2.append((4, category_id.id))
                    if m2m_list != m2m_list_2:
                        person_history.category_ids = m2m_list

                    m2m_list = []
                    for maker_id in person.marker_ids:
                        m2m_list.append((4, maker_id.id))
                    m2m_list_2 = []
                    for maker_id in person_history.marker_ids:
                        m2m_list_2.append((4, maker_id.id))
                    if m2m_list != m2m_list_2:
                        person_history.marker_ids = m2m_list

                    if person_history.responsible_id.id != person.responsible_id.id:
                        person_history.responsible_id = person.responsible_id.id

                    if person_history.caregiver_id.id != person.caregiver_id.id:
                        person_history.caregiver_id = person.caregiver_id.id

                    if person_history.ref_family_id.id != person.family_id.id:
                        person_history.ref_family_id = person.family_id.id

                    if person_history.ref_address_id.id != person.ref_address_id.id:
                        person_history.ref_address_id = person.ref_address_id.id

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', person_history.phase_id.name,
                                                 person_history.date_sign_in,
                                                 person_history.date_sign_out)

            else:

                person_history = PersonHistory.search([
                    ('person_id', '=', person.id),
                    ('date_sign_out', '=', False),
                ])

                if person_history.id is not False:
                    person_history.date_sign_out = self.date_sign_out
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', person_history.phase_id.name,
                                                 person_history.date_sign_in,
                                                 person_history.date_sign_out)

        return True
        # return self._reopen_form()
