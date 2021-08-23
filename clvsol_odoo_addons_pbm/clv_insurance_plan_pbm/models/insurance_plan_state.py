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


class InsurancePlan(models.Model):
    _inherit = 'clv.insurance_plan'

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
        for insurance_plan in self:
            if insurance_plan.is_allowed_transition(insurance_plan.state, new_state):
                insurance_plan.state = new_state
            else:
                raise UserError('Status transition (' + insurance_plan.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_draft(self):
        for insurance_plan in self:
            insurance_plan.change_state('draft')

    @api.multi
    def action_activate(self):
        for insurance_plan in self:
            insurance_plan.change_state('active')

    @api.multi
    def action_suspend(self):
        for insurance_plan in self:
            insurance_plan.change_state('suspended')

    @api.multi
    def action_cancel(self):
        for insurance_plan in self:
            insurance_plan.change_state('cancelled')
