# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxMassEdit(models.TransientModel):
    _inherit = 'clv.person_aux.mass_edit'

    ref_address_is_unavailable = fields.Boolean(
        string='Address is unavailable'
    )
    ref_address_is_unavailable_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Address is unavailable:', default=False, readonly=False, required=False
    )

    ref_address_id = fields.Many2one(
        comodel_name='clv.address',
        string='Address'
    )
    ref_address_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Address:', default=False, readonly=False, required=False
    )

    ref_address_aux_is_unavailable = fields.Boolean(
        string='Address (Aux) is unavailable'
    )
    ref_address_aux_is_unavailable_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Address (Aux) is unavailable:', default=False, readonly=False, required=False
    )

    ref_address_aux_id = fields.Many2one(
        comodel_name='clv.address',
        string='Address (Aux)'
    )
    ref_address_aux_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Address (Aux):', default=False, readonly=False, required=False
    )

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

    family_aux_is_unavailable = fields.Boolean(
        string='Family (Aux) is unavailable'
    )
    family_aux_is_unavailable_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Family (Aux) is unavailable:', default=False, readonly=False, required=False
    )

    family_aux_id = fields.Many2one(
        comodel_name='clv.address',
        string='Family (Aux)'
    )
    family_aux_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Family (Aux):', default=False, readonly=False, required=False
    )

    contact_info_is_unavailable = fields.Boolean(
        string='Contact Information is unavailable'
    )
    contact_info_is_unavailable_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Contact Information is unavailable:', default=False, readonly=False, required=False
    )
    clear_address_data = fields.Boolean(
        string='Clear Address Data'
    )

    verification_marker_ids = fields.Many2many(
        comodel_name='clv.verification.marker',
        relation='clv_person_aux_mass_edit_verification_marker_rel',
        column1='person_aux_id',
        column2='verification_marker_id',
        string='Verification Markers'
    )
    verification_marker_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Verification Markers:', default=False, readonly=False, required=False
    )

    person_aux_verification_exec = fields.Boolean(
        string='Person (Aux) Verification Execute'
    )

    @api.multi
    def do_person_aux_mass_edit(self):
        self.ensure_one()

        super().do_person_aux_mass_edit()

        for person_aux in self.person_aux_ids:

            _logger.info(u'%s %s', '>>>>>', person_aux.name)

            if self.ref_address_is_unavailable_selection == 'set':
                person_aux.ref_address_is_unavailable = self.ref_address_is_unavailable
            if self.ref_address_is_unavailable_selection == 'remove':
                person_aux.ref_address_is_unavailable = False

            if self.ref_address_id_selection == 'set':
                person_aux.ref_address_id = self.ref_address_id
            if self.ref_address_id_selection == 'remove':
                person_aux.ref_address_id = False

            if self.ref_address_aux_is_unavailable_selection == 'set':
                person_aux.ref_address_aux_is_unavailable = self.ref_address_aux_is_unavailable
            if self.ref_address_aux_is_unavailable_selection == 'remove':
                person_aux.ref_address_aux_is_unavailable = False

            if self.ref_address_aux_id_selection == 'set':
                person_aux.ref_address_aux_id = self.ref_address_aux_id
            if self.ref_address_aux_id_selection == 'remove':
                person_aux.ref_address_aux_id = False

            if self.family_is_unavailable_selection == 'set':
                person_aux.family_is_unavailable = self.family_is_unavailable
            if self.family_is_unavailable_selection == 'remove':
                person_aux.family_is_unavailable = False

            if self.family_id_selection == 'set':
                person_aux.family_id = self.family_id
            if self.family_id_selection == 'remove':
                person_aux.family_id = False

            if self.family_aux_is_unavailable_selection == 'set':
                person_aux.family_aux_is_unavailable = self.family_aux_is_unavailable
            if self.family_aux_is_unavailable_selection == 'remove':
                person_aux.family_aux_is_unavailable = False

            if self.family_aux_id_selection == 'set':
                person_aux.family_aux_id = self.family_aux_id
            if self.family_aux_id_selection == 'remove':
                person_aux.family_aux_id = False

            if self.contact_info_is_unavailable_selection == 'set':
                person_aux.contact_info_is_unavailable = self.contact_info_is_unavailable
            if self.contact_info_is_unavailable_selection == 'remove':
                person_aux.contact_info_is_unavailable = False

            if self.clear_address_data:
                person_aux.do_person_aux_clear_address_data()

            if self.verification_marker_ids_selection == 'add':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person_aux.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'remove_m2m':
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person_aux.verification_marker_ids = m2m_list
            if self.verification_marker_ids_selection == 'set':
                m2m_list = []
                for verification_marker_id in person_aux.verification_marker_ids:
                    m2m_list.append((3, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person_aux.verification_marker_ids = m2m_list
                m2m_list = []
                for verification_marker_id in self.verification_marker_ids:
                    m2m_list.append((4, verification_marker_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                person_aux.verification_marker_ids = m2m_list

            if self.person_aux_verification_exec:
                person_aux.person_aux_verification_exec()

        return True
