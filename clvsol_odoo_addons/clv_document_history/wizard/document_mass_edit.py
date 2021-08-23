# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentMassEdit(models.TransientModel):
    _inherit = 'clv.document.mass_edit'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase'
    )
    phase_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Phase:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_document_mass_edit(self):
        self.ensure_one()

        super().do_document_mass_edit()

        for document in self.document_ids:

            _logger.info(u'%s %s', '>>>>>', document.name)

            if self.phase_id_selection == 'set':
                document.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                document.phase_id = False

        return True
