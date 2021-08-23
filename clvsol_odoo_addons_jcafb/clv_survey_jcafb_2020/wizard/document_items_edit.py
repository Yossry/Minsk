# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    @api.multi
    def do_document_updt(self):
        self.ensure_one()

        super().do_document_updt()

        document = self.env['clv.document'].browse(self._context.get('active_id'))

        _logger.info(u'%s %s', '>>>>>>>>>>', document.code)

        if document.document_type_id.code == 'QAN20':
            pass

        if document.document_type_id.code == 'QDH20':
            pass

        if document.document_type_id.code == 'QMD20':
            pass

        if document.document_type_id.code == 'QSC20':
            pass

        if document.document_type_id.code == 'QSF20':
            pass

        if document.document_type_id.code == 'QSI20':
            pass

        if document.document_type_id.code == 'TAA20':
            self._do_document_updt_TAA20()

        if document.document_type_id.code == 'TAN20':
            self._do_document_updt_TAN20()

        if document.document_type_id.code == 'TCR20':
            self._do_document_updt_TCR20()

        if document.document_type_id.code == 'TDH20':
            self._do_document_updt_TDH20()

        if document.document_type_id.code == 'TID20':
            self._do_document_updt_TID20()

        if document.document_type_id.code == 'TPR20':
            pass

        if document.document_type_id.code == 'TUR20':
            pass

        if document.document_type_id.code == 'TCV20':
            self._do_document_updt_TCV20()

        return True
