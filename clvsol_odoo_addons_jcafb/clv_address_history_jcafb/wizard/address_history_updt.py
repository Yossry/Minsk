# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo import exceptions

_logger = logging.getLogger(__name__)


class AddressHistoryUpdate(models.TransientModel):
    _description = 'Address History Update'
    _name = 'clv.address.history_updt'

    def _default_address_ids(self):
        return self._context.get('active_ids')
    address_ids = fields.Many2many(
        comodel_name='clv.address',
        relation='address_history_updt_rel',
        string='Addresss',
        default=_default_address_ids
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
    def do_address_history_updt(self):
        self.ensure_one()

        AddressHistory = self.env['clv.address.history']

        for address in self.address_ids:

            if self.date_sign_out is False:
                raise exceptions.ValidationError('The "Sign out date" has not been defined!')
                return self._reopen_form()

            if self.date_sign_in is False:
                raise exceptions.ValidationError('The "Sign in date" has not been defined!')
                return self._reopen_form()

            _logger.info(u'%s %s', '>>>>>', address.name)

            if address.phase_id.id is not False:

                address_history = AddressHistory.search([
                    ('address_id', '=', address.id),
                    ('phase_id', '=', address.phase_id.id),
                    ('date_sign_out', '=', False),
                ])

                if address_history.id is False:

                    address_history_2 = AddressHistory.search([
                        ('address_id', '=', address.id),
                        ('date_sign_out', '=', False),
                    ])
                    if address_history_2.id is not False:
                        address_history_2.date_sign_out = self.date_sign_out
                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>', address_history_2.phase_id.name,
                                                     address_history_2.date_sign_in,
                                                     address_history_2.date_sign_out)

                    m2m_list = []
                    for category_id in address.category_ids:
                        m2m_list.append((4, category_id.id))
                    category_ids = m2m_list
                    m2m_list = []
                    for marker_id in address.marker_ids:
                        m2m_list.append((4, marker_id.id))
                    marker_ids = m2m_list
                    values = {
                        'phase_id': address.phase_id.id,
                        'date_sign_in': self.date_sign_in,
                        'state': address.state,
                        'reg_state': address.reg_state,
                        'employee_id': address.employee_id.id,
                        'address_id': address.id,
                        'category_ids': category_ids,
                        'marker_ids': marker_ids,
                    }
                    address_history = AddressHistory.create(values)
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', address_history.phase_id.name,
                                                 address_history.date_sign_in,
                                                 address_history.date_sign_out)

                else:

                    if address_history.state != address.state:
                        address_history.state = address.state

                    if address_history.reg_state != address.reg_state:
                        address_history.reg_state = address.reg_state

                    if address_history.employee_id.id != address.employee_id.id:
                        address_history.employee_id = address.employee_id.id

                    m2m_list = []
                    for category_id in address.category_ids:
                        m2m_list.append((4, category_id.id))
                    m2m_list_2 = []
                    for category_id in address_history.category_ids:
                        m2m_list_2.append((4, category_id.id))
                    if m2m_list != m2m_list_2:
                        address_history.category_ids = m2m_list

                    m2m_list = []
                    for maker_id in address.marker_ids:
                        m2m_list.append((4, maker_id.id))
                    m2m_list_2 = []
                    for maker_id in address_history.marker_ids:
                        m2m_list_2.append((4, maker_id.id))
                    if m2m_list != m2m_list_2:
                        address_history.marker_ids = m2m_list

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', address_history.phase_id.name,
                                                 address_history.date_sign_in,
                                                 address_history.date_sign_out)

            else:

                address_history = AddressHistory.search([
                    ('address_id', '=', address.id),
                    ('date_sign_out', '=', False),
                ])

                if address_history.id is not False:
                    address_history.date_sign_out = self.date_sign_out
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', address_history.phase_id.name,
                                                 address_history.date_sign_in,
                                                 address_history.date_sign_out)

        return True
        # return self._reopen_form()
