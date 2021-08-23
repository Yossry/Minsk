# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    #
    # TAA20
    #

    def _default_is_TAA20(self):
        active_id = self.env['clv.document'].browse(self._context.get('active_id'))
        if active_id.document_type_id.code == 'TAA20':
            is_TAA20 = True
        else:
            is_TAA20 = False
        return is_TAA20
    is_TAA20 = fields.Boolean('Is TAA20', readonly=True, default=_default_is_TAA20)

    def _default_TAA20_03_01(self):
        return self._get_default('TAA20', 'TAA20_03_01')
    TAA20_03_01 = fields.Selection([
        (u'Sim, declaro que entendi o texto acima e concordo em participar da Análise Físico-Química e Microbiológica da Água.',
         u'Sim, declaro que entendi o texto acima e concordo em participar da Análise Físico-Química e Microbiológica da Água.'),
        (u'Não concordo em participar.', u'Não concordo em participar.'),
    ], u'3.1. Consentimento', readonly=False, default=_default_TAA20_03_01)

    def _write_TAA20_03_01(self):
        self._set_value('TAA20', 'TAA20_03_01', self.TAA20_03_01)

    def _do_document_updt_TAA20(self):

        self._write_TAA20_03_01()

        return True
