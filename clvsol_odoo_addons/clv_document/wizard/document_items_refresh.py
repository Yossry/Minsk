# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsRefresh(models.TransientModel):
    _description = 'Document Items Refresh'
    _name = 'clv.document.items_refresh'

    def _default_document_ids(self):
        return self._context.get('active_ids')
    document_ids = fields.Many2many(
        comodel_name='clv.document',
        relation='clv_document_items_refresh_rel',
        string='Documents',
        default=_default_document_ids
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
    def do_document_items_refresh(self):
        self.ensure_one()

        DocumentItems = self.env['clv.document.item']

        for document in self.document_ids:

            _logger.info(u'%s %s %s', '>>>>>', document.code, document.document_type_id.name)

            items = []
            for item in document.document_type_id.item_ids:

                document_item = DocumentItems.search([
                    ('document_id', '=', document.id),
                    ('code', '=', item.code),
                ])

                if document_item.id is not False:
                    document_item.sequence = item.sequence
                else:
                    if item.document_display:
                        items.append((0, 0, {'code': item.code,
                                             'name': item.name,
                                             'sequence': item.sequence,
                                             }))

            document.item_ids = items

            _logger.info(u'%s %s', '>>>>>>>>>>', items)

        return True
