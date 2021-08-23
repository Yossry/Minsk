# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    #
    # TDH20
    #

    def _default_is_TDH20(self):
        active_id = self.env['clv.document'].browse(self._context.get('active_id'))
        if active_id.document_type_id.code == 'TDH20':
            is_TDH20 = True
        else:
            is_TDH20 = False
        return is_TDH20
    is_TDH20 = fields.Boolean('Is TDH20', readonly=True, default=_default_is_TDH20)

    def _default_TDH20_03_01(self):
        return self._get_default('TDH20', 'TDH20_03_01')
    TDH20_03_01 = fields.Selection([
        (u'Sim, declaro que entendi o texto acima e concordo em participar da Campanha Gratuita para Detecção de Diabetes, Hipertensão Arterial e Hipercolesterolemia.',
         u'Sim, declaro que entendi o texto acima e concordo em participar da Campanha Gratuita para Detecção de Diabetes, Hipertensão Arterial e Hipercolesterolemia.'),
        (u'Não concordo em participar.', u'Não concordo em participar.'),
    ], u'3.1. Consentimento', readonly=False, default=_default_TDH20_03_01)

    def _write_TDH20_03_01(self):
        self._set_value('TDH20', 'TDH20_03_01', self.TDH20_03_01)

    def _do_document_updt_TDH20(self):

        self._write_TDH20_03_01()

        return True
