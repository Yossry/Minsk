# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import UserError


class Event(models.Model):
    _inherit = 'clv.event'

    state = fields.Selection(
        [('draft', 'Unconfirmed'),
         ('confirm', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')
         ],
        string='State', default='draft', readonly=True, required=True, copy=False,
        help="If event is created, the state is 'Unconfirmed'. " +
             "If event is confirmed for the particular dates the state is set to 'Confirmed'. " +
             "If the event is over, the state is set to 'Done'. " +
             "If event is cancelled the state is set to 'Cancelled'."
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
        for event in self:
            if event.is_allowed_transition(event.state, new_state):
                event.state = new_state
            else:
                raise UserError('Status transition (' + event.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_draft(self):
        for event in self:
            event.change_state('draft')

    @api.multi
    def action_confirm(self):
        for event in self:
            event.change_state('confirm')

    @api.multi
    def action_done(self):
        for event in self:
            event.change_state('done')

    @api.multi
    def action_cancel(self):
        for event in self:
            event.change_state('cancel')
