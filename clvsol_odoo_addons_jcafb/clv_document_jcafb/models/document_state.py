# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class Document(models.Model):
    _inherit = 'clv.document'

    state = fields.Selection(
        [('new', 'New'),
         ('available', 'Available'),
         ('waiting', 'Waiting'),
         ('returned', 'Returned'),
         ('archived', 'Archived'),
         ('discarded', 'Discarded')
         ], string='Document State', default='new', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        # allowed = [
        #     ('discarded', 'new'),
        #     ('new', 'available'),
        # ]
        # return (old_state, new_state) in allowed
        return True

    @api.multi
    def change_state(self, new_state):
        for document in self:
            if document.is_allowed_transition(document.state, new_state):
                document.state = new_state
            else:
                raise UserError('Status transition (' + document.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_new(self):
        for document in self:
            document.change_state('new')

    @api.multi
    def action_available(self):
        for document in self:
            document.change_state('available')

    @api.multi
    def action_waiting(self):
        for document in self:
            document.change_state('waiting')

    @api.multi
    def action_returned(self):
        for document in self:
            document.change_state('returned')

    @api.multi
    def action_archive(self):
        for document in self:
            document.change_state('archived')

    @api.multi
    def action_discarded(self):
        for document in self:
            document.change_state('discarded')
