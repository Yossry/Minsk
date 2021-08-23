# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WeightType(models.Model):
    _name = 'weight.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "WeightType"
    
    name = fields.Char('Size',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
    shipment_method=fields.Selection([
                           ('air', 'Air'), 
                           ('land', 'Land'),
                           ('sea', 'Sea'), 
                           ('express', 'Express')],string="Shipment Method")
    weight_from=fields.Float(string='Weight From', default=0.0)
    weight_to=fields.Float(string='Weight To', default=0.0)
    uom_id=fields.Many2one('uom.uom', 
                           default=lambda self: self.env['uom.uom'].search([('name', '=', 'kg')], limit=1),readonly=True)
    uom_tow_id=fields.Many2one('uom.uom', 
                           default=lambda self: self.env['uom.uom'].search([('name', '=', 'kg')], limit=1),readonly=True)
