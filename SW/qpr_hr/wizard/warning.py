# -*- coding: utf-8 -*-
from odoo import models, api


class HRLeaveWarning(models.TransientModel):

    _name = "hr.leave.warning"
    _description = "Leave Attachment Warning"

    @api.multi
    def action_submit(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.env['hr.leave'].browse(active_ids).with_context(attachment_warning=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}
