# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentItemsEdit(models.TransientModel):
    _inherit = 'clv.document.items_edit'

    #
    # TCR20
    #

    def _default_is_TCR20(self):
        active_id = self.env['clv.document'].browse(self._context.get('active_id'))
        if active_id.document_type_id.code == 'TCR20':
            is_TCR20 = True
        else:
            is_TCR20 = False
        return is_TCR20
    is_TCR20 = fields.Boolean('Is TCR20', readonly=True, default=_default_is_TCR20)

    def _default_TCR20_03_01(self):
        return self._get_default('TCR20', 'TCR20_03_01')
    TCR20_03_01 = fields.Selection([
        (u'Concordo em participar', u'Concordo em participar'),
        (u'Não concordo em participar', u'Não concordo em participar'),
    ], u'3.1. Questionário Socioeconômico', readonly=False, default=_default_TCR20_03_01)

    def _write_TCR20_03_01(self):
        self._set_value('TCR20', 'TCR20_03_01', self.TCR20_03_01)

    def _default_TCR20_03_02(self):
        return self._get_default('TCR20', 'TCR20_03_02')
    TCR20_03_02 = fields.Selection([
        (u'Concordo em participar', u'Concordo em participar'),
        (u'Não concordo em participar', u'Não concordo em participar'),
    ], u'3.2. Exame coproparasitológico de fezes', readonly=False, default=_default_TCR20_03_02)

    def _write_TCR20_03_02(self):
        self._set_value('TCR20', 'TCR20_03_02', self.TCR20_03_02)

    def _default_TCR20_03_03(self):
        return self._get_default('TCR20', 'TCR20_03_03')
    TCR20_03_03 = fields.Selection([
        (u'Concordo em participar', u'Concordo em participar'),
        (u'Não concordo em participar', u'Não concordo em participar'),
    ], u'3.3. Swab Anal', readonly=False, default=_default_TCR20_03_03)

    def _write_TCR20_03_03(self):
        self._set_value('TCR20', 'TCR20_03_03', self.TCR20_03_03)

    def _do_document_updt_TCR20(self):

        self._write_TCR20_03_01()
        self._write_TCR20_03_02()
        self._write_TCR20_03_03()

        return True
