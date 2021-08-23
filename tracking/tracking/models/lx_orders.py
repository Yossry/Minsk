# -*- coding: utf-8 -*-

from odoo import fields, models

class LxOrders (models.Model):
    _name = 'lx.orders'
    id = fields.Integer(string="Id")
    id_report = fields.Integer(string='Id Lx',required=False)
    route_orders_id=fields.Many2one('route.order', string='Route Order', requiered=False)
    product_id = fields.Many2one('product.product', string='Product',required=False )
    code = fields.Char('Code', required=False)
    description = fields.Char('Description', required=False)
    qty = fields.Integer(string='Qty', required=False)
    price = fields.Float('Price', required=False)
    sku = fields.Char('SKU', required=False)
    promotion_id = fields.Integer(string="Promotion", required=False)
    create_date = fields.Datetime('Created on', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', index=True, readonly=True, required=False)
    write_date = fields.Datetime('Update on', index=True, readonly=True, required=False)
    write_uid = fields.Many2one('res.users', string='Updated by', index=True, readonly=True, required=False)
    tipo = fields.Selection(string='tipo',
                            selection=[('O','O'),('OE','OE'),('C','C'),('AO','AO'),('CERRAR','CERRAR')])



#    def init(self):
#        self._cr.execute("""
        

          
 #       """)
