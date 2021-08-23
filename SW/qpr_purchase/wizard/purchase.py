# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequisitionWizard(models.TransientModel):
    _name = 'purchase.requisition.wizard'
    _description = 'Purchase requisition wizard'

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequisitionWizard, self).default_get(fields)
        pr = self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
        if pr:
            res['line_ids'] = [(0, 0, {'line_id': l.id, 'description': l.description}) for l in pr.line_ids if not l.product_id]
            res['pr_id'] = pr.id
        return res

    line_ids = fields.One2many('purchase.requisition.line.wizard', 'wizard_id', string="Order Lines")
    pr_id = fields.Many2one('purchase.requisition')

    @api.multi
    def action_set_products(self):
        if not all(l.name and l.default_code for l in self.line_ids):
            raise UserError(_('Product name/code is blank'))
        for line in self.line_ids:
            product = self.env['product.product'].create({
                'name': line.name,
                'default_code': line.default_code,
                'type': 'product',
                'purchase_description': line.description})
            line.line_id.product_id = product.id

        self.pr_id.approved_by = self.env.uid
        return {'type': 'ir.actions.act_window_close'}


class PurchaseRequisitionLineWizard(models.TransientModel):
    _name = 'purchase.requisition.line.wizard'
    _description = 'Purchase requisition line wizard'

    line_id = fields.Many2one('purchase.requisition.line', string='PR line')
    name = fields.Char('Product Name')
    default_code = fields.Char('Product Code')
    description = fields.Char(required=True)
    wizard_id = fields.Many2one('purchase.requisition.wizard')
