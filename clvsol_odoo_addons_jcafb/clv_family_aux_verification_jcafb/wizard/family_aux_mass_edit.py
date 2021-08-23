# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAuxMassEdit(models.TransientModel):
    _inherit = 'clv.family_aux.mass_edit'

    verification_marker_ids = fields.Many2many(
        comodel_name='clv.verification.marker',
        relation='clv_family_aux_mass_edit_verification_marker_rel',
        column1='family_aux_id',
        column2='verification_marker_id',
        string='Verification Markers'
    )
    verification_marker_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Verification Markers:', default=False, readonly=False, required=False
    )

    family_aux_verification_exec = fields.Boolean(
        string='Family (Aux) Verification Execute'
    )

    @api.multi
    def do_family_aux_mass_edit(self):
        self.ensure_one()

        super().do_family_aux_mass_edit()

        for family_aux in self.family_aux_ids:

            _logger.info(u'%s %s', '>>>>>', family_aux.name)

            if self.verification_marker_ids_selection == 'add':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                family_aux.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'remove_m2m':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                family_aux.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'set':
                m2m_list = []
                for verification_marker_id in family_aux.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                family_aux.verification_marker_ids = m2m_list
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                family_aux.verification_marker_ids = m2m_list

            if self.family_aux_verification_exec:
                family_aux.family_aux_verification_exec()

        return True
