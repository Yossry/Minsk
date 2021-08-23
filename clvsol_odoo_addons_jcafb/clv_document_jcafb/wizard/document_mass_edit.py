# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentMassEdit(models.TransientModel):
    _inherit = 'clv.document.mass_edit'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('cancelled', 'Cancelled')
         ], string='Register State', default=False, readonly=False, required=False
    )
    reg_state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='Register State:', default=False, readonly=False, required=False
    )

    state = fields.Selection(
        [('new', 'New'),
         ('available', 'Available'),
         ('waiting', 'Waiting'),
         ('returned', 'Returned'),
         ('archived', 'Archived'),
         ('discarded', 'Discarded')
         ], string='Document State', default=False, readonly=False, required=False
    )
    state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='Document State:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_document_mass_edit(self):
        self.ensure_one()

        super().do_document_mass_edit()

        for document in self.document_ids:

            _logger.info(u'%s %s', '>>>>>', document.name)

            if self.reg_state_selection == 'set':
                document.reg_state = self.reg_state
            if self.reg_state_selection == 'remove':
                document.reg_state = False

            if self.state_selection == 'set':
                document.state = self.state
            if self.state_selection == 'remove':
                document.state = False

        return True
