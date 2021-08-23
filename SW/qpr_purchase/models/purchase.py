# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    name = fields.Char(string='Reference #')
    user_id = fields.Many2one(string='Requested By')
    date_end = fields.Datetime(string='Request Deadline')
    schedule_date = fields.Date(string='Expected Delivery Date')
    origin = fields.Char(string='Reason ref.')
    department_id = fields.Many2one('hr.department', string='Department')
    reviewed_by = fields.Many2one('res.users', string='Reviewed By', copy=False)
    approved_by = fields.Many2one('res.users', string='Approved By', copy=False)
    type_id = fields.Many2one(string='Request Type')
    reason = fields.Text(string='Reason For Requisition')

    @api.onchange('user_id')
    def onchange_user_id(self):
        self.department_id = self.user_id.employee_ids and self.user_id.employee_ids[0].department_id.id

    @api.multi
    def action_review(self):
        self.ensure_one()
        self.reviewed_by = self.env.uid
        msg = _('This order reviewed by - %s') % (self.env.user.name)
        self.message_post(body=msg)

    @api.multi
    def action_approve(self):
        self.ensure_one()
        if all(l.product_id for l in self.line_ids):
            self.approved_by = self.env.uid
            return True
        action = self.env.ref('qpr_purchase.action_purchase_requisition_wizard').read()[0]
        return action


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    description = fields.Char(required=True)
    product_id = fields.Many2one(required=False)
    qty_available = fields.Float(related='product_id.qty_available', string='Qty On Hand', readonly=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        name = self.product_id.display_name
        if self.product_id.description_purchase:
            name += '\n' + self.product_id.description_purchase
        self.description = name

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res['name'] = self.description
        return res


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"
    _description = "Request For Material/Service Type"

    name = fields.Char(string='Request For Material/Service Type')
    exclusive = fields.Selection(string='Request For Material/Service Selection Type')


