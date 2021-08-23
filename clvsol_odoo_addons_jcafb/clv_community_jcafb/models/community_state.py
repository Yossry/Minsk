# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import UserError


class Community(models.Model):
    _inherit = 'clv.community'

    state = fields.Selection(
        [('draft', 'Unconfirmed'),
         ('confirm', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')
         ],
        string='State', default='draft', readonly=True, required=True, copy=False,
        help="If community is created, the state is 'Unconfirmed'. " +
             "If community is confirmed for the particular dates the state is set to 'Confirmed'. " +
             "If the community is over, the state is set to 'Done'. " +
             "If community is cancelled the state is set to 'Cancelled'."
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        # allowed = [
        #     ('cancel', 'draft'),
        # ]
        # return (old_state, new_state) in allowed
        return True

    @api.multi
    def change_state(self, new_state):
        for community in self:
            if community.is_allowed_transition(community.state, new_state):
                community.state = new_state
            else:
                raise UserError('Status transition (' + community.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_draft(self):
        for community in self:
            community.change_state('draft')

    @api.multi
    def action_confirm(self):
        for community in self:
            community.change_state('confirm')

    @api.multi
    def action_done(self):
        for community in self:
            community.change_state('done')

    @api.multi
    def action_cancel(self):
        for community in self:
            community.change_state('cancel')
