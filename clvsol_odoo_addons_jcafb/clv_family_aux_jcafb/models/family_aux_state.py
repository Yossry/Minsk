# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class FamilyAux(models.Model):
    _inherit = 'clv.family_aux'

    state = fields.Selection(
        [('new', 'New'),
         ('available', 'Available'),
         ('waiting', 'Waiting'),
         ('selected', 'Selected'),
         ('unselected', 'Unselected'),
         ('unavailable', 'Unavailable'),
         ('unknown', 'Unknown')
         ], string='Family State', default='new', readonly=True, required=True
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
        for family_aux in self:
            if family_aux.is_allowed_transition(family_aux.state, new_state):
                family_aux.state = new_state
            else:
                raise UserError('Status transition (' + family_aux.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_new(self):
        for family_aux in self:
            family_aux.change_state('new')

    @api.multi
    def action_available(self):
        for family_aux in self:
            family_aux.change_state('available')

    @api.multi
    def action_waiting(self):
        for family_aux in self:
            family_aux.change_state('waiting')

    @api.multi
    def action_select(self):
        for family_aux in self:
            family_aux.change_state('selected')

    @api.multi
    def action_unselect(self):
        for family_aux in self:
            family_aux.change_state('unselected')

    @api.multi
    def action_unavailable(self):
        for family_aux in self:
            family_aux.change_state('unavailable')

    @api.multi
    def action_unknown(self):
        for family_aux in self:
            family_aux.change_state('unknown')
