# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

'''
Reference: http://help.openerp.com/question/18704/hide-menu-for-existing-group/

There are actually0-6 numbers for representing each job for a many2many/ one2many field

    (0, 0, { values }) -- link to a new record that needs to be created with the given values dictionary
    (1, ID, { values }) -- update the linked record with id = ID (write values on it)
    (2, ID) -- remove and delete the linked record with id = ID (calls unlink on ID, that will delete the
               object completely, and the link to it as well)
    (3, ID) -- cut the link to the linked record with id = ID (delete the relationship between the two
               objects but does not delete the target object itself)
    (4, ID) -- link to existing record with id = ID (adds a relationship)
    (5) -- unlink all (like using (3,ID) for all linked records)
    (6, 0, [IDs]) -- replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)
'''

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestRequestMassEdit(models.TransientModel):
    _description = 'Lab Test Request Mass Edit'
    _name = 'clv.lab_test.request.mass_edit'

    def _default_lab_test_request_ids(self):
        return self._context.get('active_ids')
    lab_test_request_ids = fields.Many2many(
        comodel_name='clv.lab_test.request',
        relation='clv_lab_test_request_mass_edit_rel',
        string='Lab Test Requests',
        default=_default_lab_test_request_ids
    )

    date_request = fields.Date(string='Date of the Request', default=False, readonly=False, required=False)
    date_request_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Date of the Request:', default=False, readonly=False, required=False
    )

    @api.model
    def referenceable_models(self):
        return [(ref.model, ref.name) for ref in self.env['clv.referenceable.model'].search([
            ('base_model', '=', 'clv.lab_test.request'),
        ])]

    ref_id = fields.Reference(
        selection='referenceable_models',
        string='Refers to')
    ref_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Refers to:', default=False, readonly=False, required=False
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
    def do_lab_test_request_mass_edit(self):
        self.ensure_one()

        for lab_test_request in self.lab_test_request_ids:

            _logger.info(u'%s %s', '>>>>>', lab_test_request.code)

            if self.date_request_selection == 'set':
                lab_test_request.date_request = self.date_request
            if self.date_request_selection == 'remove':
                lab_test_request.date_request = False

            if self.ref_id_selection == 'set':
                lab_test_request.ref_id = self.ref_id
            if self.ref_id_selection == 'remove':
                lab_test_request.ref_id = False

        return True
