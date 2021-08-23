# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class LabTestResult(models.Model):
    _inherit = 'clv.lab_test.result'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('cancelled', 'Cancelled')
         ], string='Register State', default='draft', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition_reg_state(self, old_reg_state, new_reg_state):
        # allowed = [
        #     ('cancelled', 'draft'),
        # ]
        # return (old_reg_state, new_reg_state) in allowed
        return True

    @api.multi
    def change_reg_state(self, new_reg_state):
        for lab_test_result in self:
            if lab_test_result.is_allowed_transition_reg_state(lab_test_result.reg_state, new_reg_state):
                lab_test_result.reg_state = new_reg_state
            else:
                raise UserError(
                    'Status transition (' + lab_test_result.reg_state + ', ' + new_reg_state + ') is not allowed!'
                )

    @api.multi
    def action_draft(self):
        for lab_test_result in self:
            lab_test_result.change_reg_state('draft')

    @api.multi
    def action_revised(self):
        for lab_test_result in self:
            lab_test_result.change_reg_state('revised')

    @api.multi
    def action_done(self):
        for lab_test_result in self:
            lab_test_result.change_reg_state('done')

    @api.multi
    def action_cancel(self):
        for lab_test_result in self:
            lab_test_result.change_reg_state('cancelled')
