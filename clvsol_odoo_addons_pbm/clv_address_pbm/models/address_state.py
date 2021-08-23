# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class Address(models.Model):
    _inherit = 'clv.address'

    state = fields.Selection(
        [('new', 'New'),
         ('available', 'Available'),
         ('waiting', 'Waiting'),
         ('selected', 'Selected'),
         ('unselected', 'Unselected'),
         ('unavailable', 'Unavailable'),
         ('unknown', 'Unknown'),
         ('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('canceled', 'Canceled')
         ], string='Address State', default='new', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        # allowed = [
        #     ('unavailable', 'new'),
        # ]
        # return (old_state, new_state) in allowed
        return True

    @api.multi
    def change_state(self, new_state):
        for address in self:
            if address.is_allowed_transition(address.state, new_state):
                address.state = new_state
            else:
                raise UserError('Status transition (' + address.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_new(self):
        for address in self:
            address.change_state('new')

    @api.multi
    def action_available(self):
        for address in self:
            address.change_state('available')

    @api.multi
    def action_waiting(self):
        for address in self:
            address.change_state('waiting')

    @api.multi
    def action_select(self):
        for address in self:
            address.change_state('selected')

    @api.multi
    def action_unselect(self):
        for address in self:
            address.change_state('unselected')

    @api.multi
    def action_unavailable(self):
        for address in self:
            address.change_state('unavailable')

    @api.multi
    def action_unknown(self):
        for address in self:
            address.change_state('unknown')

    @api.multi
    def action_draft(self):
        for address in self:
            address.change_reg_state('draft')

    @api.multi
    def action_revised(self):
        for address in self:
            address.change_reg_state('revised')

    @api.multi
    def action_done(self):
        for address in self:
            address.change_reg_state('done')

    @api.multi
    def action_cancel(self):
        for address in self:
            address.change_reg_state('canceled')
