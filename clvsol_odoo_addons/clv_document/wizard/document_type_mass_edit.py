# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentTypeMassEdit(models.TransientModel):
    _description = 'Document Type Mass Edit'
    _name = 'clv.document.type.mass_edit'

    def _default_document_type_ids(self):
        return self._context.get('active_ids')
    document_type_ids = fields.Many2many(
        comodel_name='clv.document.type',
        relation='clv_document_type_mass_edit_rel',
        string='Document Types',
        default=_default_document_type_ids
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
    def do_document_type_mass_edit(self):
        self.ensure_one()

        for document_type in self.document_type_ids:

            _logger.info(u'%s %s', '>>>>>', document_type.name)

        return True
