# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, field_vals):
        res = super(SaleOrder, self).default_get(field_vals)
        if res.get('opportunity_id'):
            lead = self.env['crm.lead'].browse(res['opportunity_id'])
            res['order_line'] = [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.name,
                'product_uom_qty': l.qty,
                'product_uom': l.uom_id.id,
                'price_unit': l.price}) for l in lead.line_ids]
        return res
