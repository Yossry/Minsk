# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('verified', 'Verified'),
         ('ready', 'Ready'),
         ('done', 'Done'),
         ('canceled', 'Canceled')
         ], string='Register State', default='draft', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition_reg_state(self, old_reg_state, new_reg_state):
        # allowed = [
        #     ('canceled', 'draft'),
        # ]
        # return (old_reg_state, new_reg_state) in allowed
        return True

    @api.multi
    def change_reg_state(self, new_reg_state):
        for person_aux in self:
            if person_aux.is_allowed_transition_reg_state(person_aux.reg_state, new_reg_state):
                person_aux.reg_state = new_reg_state
            else:
                raise UserError('Status transition (' + person_aux.reg_state + ', ' + new_reg_state +
                                ') is not allowed!')

    @api.multi
    def action_draft(self):
        for person_aux in self:
            person_aux.change_reg_state('draft')

    @api.multi
    def action_revised(self):
        for person_aux in self:
            person_aux.change_reg_state('revised')

    @api.multi
    def action_verified(self):
        for person_aux in self:
            person_aux.change_reg_state('verified')

    @api.multi
    def action_ready(self):
        for person_aux in self:
            person_aux.change_reg_state('ready')

    @api.multi
    def action_done(self):
        for person_aux in self:
            person_aux.change_reg_state('done')

    @api.multi
    def action_cancel(self):
        for person_aux in self:
            person_aux.change_reg_state('canceled')
