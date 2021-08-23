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

from openerp import api, fields, models
from openerp.exceptions import UserError


class InsuredGroup(models.Model):
    _inherit = 'clv.insured_group'

    state = fields.Selection(
        [('draft', 'New'),
         ('active', 'Active'),
         ('suspended', 'Suspended'),
         ('cancelled', 'Cancelled'),
         ], string='State', default='draft', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        # allowed = [
        #     ('old_state_1', 'new_state_1'),
        #     ('old_state_2', 'new_state_2'),
        # ]
        # return (old_state, new_state) in allowed
        return True

    @api.multi
    def change_state(self, new_state):
        for insured_group in self:
            if insured_group.is_allowed_transition(insured_group.state, new_state):
                insured_group.state = new_state
            else:
                raise UserError('Status transition (' + insured_group.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_draft(self):
        for insured_group in self:
            insured_group.change_state('draft')

    @api.multi
    def action_activate(self):
        for insured_group in self:
            insured_group.change_state('active')

    @api.multi
    def action_suspend(self):
        for insured_group in self:
            insured_group.change_state('suspended')

    @api.multi
    def action_cancel(self):
        for insured_group in self:
            insured_group.change_state('cancelled')
