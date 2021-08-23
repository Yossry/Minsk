# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    # def _default_person_id(self):
    #     return self.env['clv.document'].browse(self._context.get('active_id')).person_id
    # person_id = fields.Many2one(
    #     comodel_name='clv.person',
    #     string='Person',
    #     readonly=True,
    #     default=_default_person_id
    # )

    # def _default_address_id(self):
    #     return self.env['clv.document'].browse(self._context.get('active_id')).address_id
    # address_id = fields.Many2one(
    #     comodel_name='clv.address',
    #     string='Address',
    #     readonly=True,
    #     default=_default_address_id
    # )

    @api.multi
    def do_document_updt(self):
        self.ensure_one()

        super().do_document_updt()

        document = self.env['clv.document'].browse(self._context.get('active_id'))

        _logger.info(u'%s %s', '>>>>>>>>>>', document.code)

        return True
