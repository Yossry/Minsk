# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class MediaFile(models.Model):
    _inherit = 'clv.mfile'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('canceled', 'Canceled')
         ], string='Register State', default='draft', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition_reg_state(self, old_reg_state, new_reg_state):
        # allowed = [
        #     ('canceled', 'draft'),
        #     ('draft', 'revised'),
        #     ('done', 'revised'),
        #     ('revised', 'done'),
        #     ('draft', 'canceled'),
        #     ('revised', 'canceled')
        # ]
        # return (old_reg_state, new_reg_state) in allowed
        return True

    @api.multi
    def change_reg_state(self, new_reg_state):
        for mfile in self:
            if mfile.is_allowed_transition_reg_state(mfile.reg_state, new_reg_state):
                mfile.reg_state = new_reg_state
            else:
                raise UserError('Status transition (' + mfile.reg_state + ', ' + new_reg_state + ') is not allowed!')

    @api.multi
    def action_draft(self):
        for mfile in self:
            mfile.change_reg_state('draft')

    @api.multi
    def action_revised(self):
        for mfile in self:
            mfile.change_reg_state('revised')

    @api.multi
    def action_done(self):
        for mfile in self:
            mfile.change_reg_state('done')

    @api.multi
    def action_cancel(self):
        for mfile in self:
            mfile.change_reg_state('canceled')
