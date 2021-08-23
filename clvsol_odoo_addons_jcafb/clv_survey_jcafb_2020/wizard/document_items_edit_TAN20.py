# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    #
    # TAN20
    #

    def _default_is_TAN20(self):
        active_id = self.env['clv.document'].browse(self._context.get('active_id'))
        if active_id.document_type_id.code == 'TAN20':
            is_TAN20 = True
        else:
            is_TAN20 = False
        return is_TAN20
    is_TAN20 = fields.Boolean('Is TAN20', readonly=True, default=_default_is_TAN20)

    def _default_TAN20_03_01(self):
        return self._get_default('TAN20', 'TAN20_03_01')
    TAN20_03_01 = fields.Selection([
        (u'Sim, declaro que entendi o texto acima e concordo em participar da Campanha Gratuita para Detecção de Anemia.',
         u'Sim, declaro que entendi o texto acima e concordo em participar da Campanha Gratuita para Detecção de Anemia.'),
        (u'Não concordo em participar.', u'Não concordo em participar.'),
    ], u'3.1. Consentimento', readonly=False, default=_default_TAN20_03_01)

    def _write_TAN20_03_01(self):
        self._set_value('TAN20', 'TAN20_03_01', self.TAN20_03_01)

    def _do_document_updt_TAN20(self):

        self._write_TAN20_03_01()

        return True
