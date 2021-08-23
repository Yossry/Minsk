# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _get_opportunity_type(self):
        return [
            ('new', 'New Business'),
            ('special', 'Special'),
            ('it_related', 'IT-Related'),
            ('advertising', 'Advertising'),
            ('subscription', 'Subscription'),
            ('gifts', 'Gifts'),
            ('premiums', 'Premiums'),
        ]
    opportunity_type = fields.Selection(selection=_get_opportunity_type)
    approval_state = fields.Selection([
        ('pm', 'PM Approval'),
        ('am', 'AM Approval'),
        ('cxo', 'CEO Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected')],
        string='Approval State', track_visibility='onchange', copy=False, default='pm')
    reference_code = fields.Char('Reference Code')
    show_approval_btn = fields.Boolean(compute='_show_approval_btn')
    line_ids = fields.One2many('lead.line', 'lead_id', string='Product List')

    @api.multi
    def action_reject(self):
        self.approval_state = 'reject'
        message = _('Opportunity has been rejected by %s') % (self.env.user.partner_id.display_name)
        return self.message_post(body=message)

    @api.multi
    def action_approve(self):
        self.ensure_one()
        is_cxo = self.env.user.has_group('qpr_crm.group_cxo')
        is_pm = self.env.user.has_group('project.group_project_manager')
        is_am = self.env.user.has_group('account.group_account_manager')
        state = self.approval_state
        if state == 'pm' and is_pm:
            self.approval_state = 'am'
        elif state == 'am' and is_am:
            self.approval_state = 'cxo'
        elif state == 'cxo' and is_cxo:
            self.approval_state = 'approved'
        message = _('Opportunity has been approved by %s') % (self.env.user.partner_id.display_name)
        return self.message_post(body=message)

    @api.multi
    def _show_approval_btn(self):
        is_pm = self.env.user.has_group('project.group_project_manager')
        is_am = self.env.user.has_group('account.group_account_manager')
        is_cxo = self.env.user.has_group('qpr_crm.group_cxo')
        for lead in self:
            if lead.opportunity_type in ['new', 'special', 'it_related']:
                if lead.approval_state == 'pm' and is_pm:
                    lead.show_approval_btn = True
                elif lead.approval_state == 'am' and is_am:
                    lead.show_approval_btn = True
                elif lead.approval_state == 'cxo' and is_cxo:
                    lead.show_approval_btn = True

            elif lead.opportunity_type in ['advertising', 'subscription', 'gifts', 'premiums']:
                if lead.approval_state == 'cxo' and is_cxo:
                    lead.show_approval_btn = True

    @api.onchange('opportunity_type')
    def onchange_opportunity_type(self):
        if self.opportunity_type in ['new', 'special', 'it_related']:
            self.approval_state = 'pm'
        else:
            self.approval_state = 'cxo'

    @api.multi
    def action_reopen(self):
        self.ensure_one()
        self.write({'opportunity_type': 'advertising', 'approval_state': 'cxo'})
        return True


class LeadLine(models.Model):
    _name = 'lead.line'
    _description = 'Opportunity Line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    lead_id = fields.Many2one('crm.lead', string='Lead')
