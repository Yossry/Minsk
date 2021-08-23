# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    #
    # TCV20
    #

    def _default_is_TCV20(self):
        active_id = self.env['clv.document'].browse(self._context.get('active_id'))
        if active_id.document_type_id.code == 'TCV20':
            is_TCV20 = True
        else:
            is_TCV20 = False
        return is_TCV20
    is_TCV20 = fields.Boolean('Is TCV20', readonly=True, default=_default_is_TCV20)

    def _default_TCV20_03_01(self):
        return self._get_default('TCV20', 'TCV20_03_01')
    TCV20_03_01 = fields.Selection([
        (u'Sim, declaro que entendi o texto acima e concordo em participar.',
         u'Sim, declaro que entendi o texto acima e concordo em participar.'),
        (u'Não concordo em participar.', u'Não concordo em participar.'),
    ], u'3.1. Consentimento', readonly=False, default=_default_TCV20_03_01)

    def _write_TCV20_03_01(self):
        self._set_value('TCV20', 'TCV20_03_01', self.TCV20_03_01)

    def _do_document_updt_TCV20(self):

        self._write_TCV20_03_01()

        return True
