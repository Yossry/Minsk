# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsOkSetUp(models.TransientModel):
    _description = 'Document Items Ok Setup'
    _name = 'clv.document.items_ok_setup'

    def _default_document_ids(self):
        return self._context.get('active_ids')
    document_ids = fields.Many2many(
        comodel_name='clv.document',
        relation='clv_document_items_ok_setup_rel',
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
    def do_document_items_ok_setup(self):
        self.ensure_one()

        for document in self.document_ids:

            _logger.info(u'%s %s %s', '>>>>>', document.code, document.document_type_id.name)

            value_count = 0
            for item in document.item_ids:

                if item.value is not False:
                    value_count += 1
                    # break

            if value_count > 0:
                document.items_ok = True
            else:
                document.items_ok = False

            _logger.info(u'%s %s %s', '>>>>>>>>>>', document.items_ok, value_count)

        return True
