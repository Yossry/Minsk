# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonMassEdit(models.TransientModel):
    _inherit = 'clv.person.mass_edit'

    family_is_unavailable = fields.Boolean(
        string='Family is unavailable'
    )
    family_is_unavailable_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Family is unavailable:', default=False, readonly=False, required=False
    )

    family_id = fields.Many2one(
        comodel_name='clv.address',
        string='Family'
    )
    family_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Family:', default=False, readonly=False, required=False
    )

    verification_marker_ids = fields.Many2many(
        comodel_name='clv.verification.marker',
        relation='clv_person_mass_edit_verification_marker_rel',
        column1='person_id',
        column2='verification_marker_id',
        string='Verification Markers'
    )
    verification_marker_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Verification Markers:', default=False, readonly=False, required=False
    )

    person_verification_exec = fields.Boolean(
        string='Person Verification Execute'
    )

    @api.multi
    def do_person_mass_edit(self):
        self.ensure_one()

        super().do_person_mass_edit()

        for person in self.person_ids:

            _logger.info(u'%s %s', '>>>>>', person.name)

            if self.family_is_unavailable_selection == 'set':
                person.family_is_unavailable = self.family_is_unavailable
            if self.family_is_unavailable_selection == 'remove':
                person.family_is_unavailable = False

            if self.family_id_selection == 'set':
                person.family_id = self.family_id
            if self.family_id_selection == 'remove':
                person.family_id = False

            if self.verification_marker_ids_selection == 'add':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'remove_m2m':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'set':
                m2m_list = []
                for verification_marker_id in person.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person.verification_marker_ids = m2m_list
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person.verification_marker_ids = m2m_list

            if self.person_verification_exec:
                person.person_verification_exec()

        return True
