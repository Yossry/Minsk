# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class PartnerProcess(models.TransientModel):
    _name = "res.partner.process"
    _description = "Procesar"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))
    count = fields.Integer(default=_count, string='# of Rutas')

    @api.multi
    def process(self):
        partner = self.env['res.partner'].browse(self._context.get('active_ids', []))
        total = len(partner)
        route = self.env['route.order']
        for p in partner:
            shipping= self.env['res.partner'].search([('parent_id','=',p.id),('type','=','delivery')], limit=1)
            shipping_id = False
            if shipping:
                shipping_id = shipping.id
            else:
                shipping_id = p.id

            vals = {
                'name': 'New',
                'partner_id': p.id,
                'partner_shipping_id':shipping_id,
                'manage_id':p.zona.user_id.id,
                'zone_id': p.zona.id
            }
            route.create(vals)

    @api.multi
    def process2(self):
        partner = self.env['res.partner'].browse(self._context.get('active_ids', []))
        total = len(partner)
        route = self.env['route.order']
        for p in partner:
            shipping= self.env['res.partner'].search([('parent_id','=',p.id),('type','=','delivery')], limit=1)
            shipping_id = False
            if shipping:
                shipping_id = shipping.id
            else:
                shipping_id = p.id

            vals = {
                'name': 'New',
                'partner_id': p.id,
                'partner_shipping_id':shipping_id,
                'manage_id':p.zonalac.user_id.id,
                'zone_id': p.zonalac.id
            }
            route.create(vals)