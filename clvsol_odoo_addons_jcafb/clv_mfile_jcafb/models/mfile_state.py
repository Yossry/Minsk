# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import UserError


class Address(models.Model):
    _inherit = 'clv.mfile'

    state = fields.Selection(
        [('new', 'New'),
         ('returned', 'Returned'),
         ('checked', 'Checked'),
         ('validated', 'Validated'),
         ('imported', 'Imported'),
         ('archived', 'Archived'),
         ('discarded', 'Discarded'),
         ], string='State', default='new', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        return True

    @api.multi
    def change_state(self, new_state):
        for mfile in self:
            if mfile.is_allowed_transition(mfile.state, new_state):
                mfile.state = new_state
            else:
                raise UserError('Status transition (' + mfile.state + ', ' + new_state + ') is not allowed!')

    @api.multi
    def action_new(self):
        for mfile in self:
            mfile.change_state('new')

    @api.multi
    def action_returned(self):
        for mfile in self:
            mfile.change_state('returned')

    @api.multi
    def action_checked(self):
        for mfile in self:
            mfile.change_state('checked')

    @api.multi
    def action_validated(self):
        for mfile in self:
            mfile.change_state('validated')

    @api.multi
    def action_imported(self):
        for mfile in self:
            mfile.change_state('imported')

    @api.multi
    def action_archived(self):
        for mfile in self:
            mfile.change_state('archived')

    @api.multi
    def action_discarded(self):
        for mfile in self:
            mfile.change_state('discarded')
