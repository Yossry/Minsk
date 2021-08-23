# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class LeadApprovalWizard(models.TransientModel):
    _name = 'lead.approval.wizard'
    _description = 'Lead Approval'

    name = fields.Text(required=True)

    @api.multi
    def action_approve(self):
        lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        lead.action_approve()
        message = 'Approved Note --> \n'
        message += self.name
        lead.message_post(body=message)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reject(self):
        lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        lead.action_reject()
        message = 'Rejected Note --> \n'
        message += self.name
        lead.message_post(body=message)
        return {'type': 'ir.actions.act_window_close'}
