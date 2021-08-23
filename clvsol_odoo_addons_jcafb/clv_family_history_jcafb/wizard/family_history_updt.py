# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo import exceptions

_logger = logging.getLogger(__name__)


class FamilyHistoryUpdate(models.TransientModel):
    _description = 'Family History Update'
    _name = 'clv.family.history_updt'

    def _default_family_ids(self):
        return self._context.get('active_ids')
    family_ids = fields.Many2many(
        comodel_name='clv.family',
        relation='family_history_updt_rel',
        string='Families',
        default=_default_family_ids
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
    def do_family_history_updt(self):
        self.ensure_one()

        FamilyHistory = self.env['clv.family.history']

        for family in self.family_ids:

            if self.date_sign_out is False:
                raise exceptions.ValidationError('The "Sign out date" has not been defined!')
                return self._reopen_form()

            if self.date_sign_in is False:
                raise exceptions.ValidationError('The "Sign in date" has not been defined!')
                return self._reopen_form()

            _logger.info(u'%s %s', '>>>>>', family.name)

            if family.phase_id.id is not False:

                family_history = FamilyHistory.search([
                    ('family_id', '=', family.id),
                    ('phase_id', '=', family.phase_id.id),
                    ('date_sign_out', '=', False),
                ])

                if family_history.id is False:

                    family_history_2 = FamilyHistory.search([
                        ('family_id', '=', family.id),
                        ('date_sign_out', '=', False),
                    ])
                    if family_history_2.id is not False:
                        family_history_2.date_sign_out = self.date_sign_out
                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>', family_history_2.phase_id.name,
                                                     family_history_2.date_sign_in,
                                                     family_history_2.date_sign_out)

                    m2m_list = []
                    for category_id in family.category_ids:
                        m2m_list.append((4, category_id.id))
                    category_ids = m2m_list
                    m2m_list = []
                    for marker_id in family.marker_ids:
                        m2m_list.append((4, marker_id.id))
                    marker_ids = m2m_list
                    values = {
                        'phase_id': family.phase_id.id,
                        'date_sign_in': self.date_sign_in,
                        'state': family.state,
                        'reg_state': family.reg_state,
                        'employee_id': family.employee_id.id,
                        'family_id': family.id,
                        'category_ids': category_ids,
                        'marker_ids': marker_ids,
                        'ref_address_id': family.ref_address_id.id,
                    }
                    family_history = FamilyHistory.create(values)
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', family_history.phase_id.name,
                                                 family_history.date_sign_in,
                                                 family_history.date_sign_out)

                else:

                    if family_history.state != family.state:
                        family_history.state = family.state

                    if family_history.reg_state != family.reg_state:
                        family_history.reg_state = family.reg_state

                    if family_history.employee_id.id != family.employee_id.id:
                        family_history.employee_id = family.employee_id.id

                    m2m_list = []
                    for category_id in family.category_ids:
                        m2m_list.append((4, category_id.id))
                    m2m_list_2 = []
                    for category_id in family_history.category_ids:
                        m2m_list_2.append((4, category_id.id))
                    if m2m_list != m2m_list_2:
                        family_history.category_ids = m2m_list

                    m2m_list = []
                    for maker_id in family.marker_ids:
                        m2m_list.append((4, maker_id.id))
                    m2m_list_2 = []
                    for maker_id in family_history.marker_ids:
                        m2m_list_2.append((4, maker_id.id))
                    if m2m_list != m2m_list_2:
                        family_history.marker_ids = m2m_list

                    if family_history.ref_address_id.id != family.ref_address_id.id:
                        family_history.ref_address_id = family.ref_address_id.id

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', family_history.phase_id.name,
                                                 family_history.date_sign_in,
                                                 family_history.date_sign_out)

            else:

                family_history = FamilyHistory.search([
                    ('family_id', '=', family.id),
                    ('date_sign_out', '=', False),
                ])

                if family_history.id is not False:
                    family_history.date_sign_out = self.date_sign_out
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', family_history.phase_id.name,
                                                 family_history.date_sign_in,
                                                 family_history.date_sign_out)

        return True
        # return self._reopen_form()
