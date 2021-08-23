# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import shutil

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MfileVefify(models.TransientModel):
    _name = 'clv.mfile.verify'

    def _default_mfile_ids(self):
        return self._context.get('active_ids')
    mfile_ids = fields.Many2many(
        comodel_name='clv.mfile',
        relation='clv_mfile_mfile_verify_rel',
        string='Media Files',
        default=_default_mfile_ids
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
    def do_mfile_verify(self):
        self.ensure_one()

        for mfile in self.mfile_ids:

            _logger.info(u'%s %s', '>>>>>', mfile.name)

            if (mfile.address_id is not False) and \
               (mfile.document_id.ref_id is not False):
                if mfile.address_id.code != mfile.document_id.ref_id.code:
                    _logger.error(u'%s %s [%s]', '>>>>>>>>>> (address):',
                                  mfile.address_id.name,
                                  mfile.document_id.ref_id.name)

        return True
