# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MediaFileMassEdit(models.TransientModel):
    _inherit = 'clv.mfile.mass_edit'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('canceled', 'Canceled')
         ], string='Register State', default=False, readonly=False, required=False
    )
    reg_state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='Register State:', default=False, readonly=False, required=False
    )

    state = fields.Selection(
        [('new', 'New'),
         ('getting', 'Getting'),
         ('stored', 'Stored'),
         ('checked', 'Checked'),
         ('in_use', 'In Use'),
         ('used', 'Used'),
         ('deleted', 'Deleted'),
         ], string='State', default=False, readonly=False, required=False
    )
    state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='State:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_mfile_mass_edit(self):
        self.ensure_one()

        super().do_mfile_mass_edit()

        for mfile in self.mfile_ids:

            _logger.info(u'%s %s', '>>>>>', mfile.name)

            if self.reg_state_selection == 'set':
                mfile.reg_state = self.reg_state
            if self.reg_state_selection == 'remove':
                mfile.reg_state = False

            if self.state_selection == 'set':
                mfile.state = self.state
            if self.state_selection == 'remove':
                mfile.state = False

        return True
