# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CardUpdate(models.TransientModel):
    _inherit = 'clv.card.updt'

    state = fields.Selection(
        [('draft', 'New'),
         ('processing', 'Processing'),
         ('active', 'Active'),
         ('suspended', 'Suspended'),
         ('cancelled', 'Cancelled'),
         ], string='State', default=False, readonly=False, required=False
    )
    state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='State', default=False, readonly=False, required=False
    )

    @api.multi
    def do_card_updt(self):
        self.ensure_one()

        super(CardUpdate, self).do_card_updt()

        for card in self.card_ids:

            _logger.info(u'%s %s', '>>>>>', card.name)

            if self.state_selection == 'set':
                card.state = self.state
            if self.state_selection == 'remove':
                card.state = False

        return True
