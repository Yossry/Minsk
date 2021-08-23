# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Document_typeMassEdit(models.TransientModel):
    _inherit = 'clv.document.type.mass_edit'

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
    def do_document_type_mass_edit(self):
        self.ensure_one()

        super().do_document_type_mass_edit()

        for document_type in self.document_type_ids:

            _logger.info(u'%s %s', '>>>>>', document_type.name)

            if self.phase_id_selection == 'set':
                document_type.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                document_type.phase_id = False

        return True
