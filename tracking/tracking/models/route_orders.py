## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
import logging
_logger = logging.getLogger(__name__)

class RouteOrder(models.Model):
    _name ='route.order'
    name = fields.Char(string="Nombre", required=True,index=True, copy=False, default='New',readonly=True)
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True)
    partner_shipping_id = fields.Many2one('res.partner', string='Dirección Envío', required=True)
    priority = fields.Selection([
        ('C', 'Critica'),
        ('A', 'Alta'),
        ('N', 'Normal'),
        ('B', 'Baja')
        ], string='Prioridad',default='N')
    date_order = fields.Datetime(string='Agendada', default=fields.Datetime.now)
    manage_id = fields.Many2one('hr.employee', string="Encargado", required=True)
    comentary = fields.Text('Comentarios')
    type = fields.Selection([
        ('ENTREGA','Entrega'),
	('VENTA','Venta')
        ], string='Type', copy=False, default='VENTA')
    state = fields.Selection([
        ('0', 'Sin sincronizar'),
        ('1', 'Sin descargar'),
        ('2', 'Pendiente'),
        ('3', 'Incompleta'),
        ('4', 'Completa'),
        ('5', 'Cancelada'),
        ('6', 'Cerrado'),
        ('11', 'Error')
        ], string='Estado', copy=False, default='0', readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta', required=False, readonly=True )
    stock_picking_id = fields.Many2one('stock.picking', string='Albaran de salida', required=False, readonly=True)
    amount = fields.Float(digits=(32, 32),string='Monto Debe',defualt=0.0)
    zone_id = fields.Many2one('res.zona', string="Zona", required=True)
    sync_error = fields.Char(string="Sync Error", readonly=True)
    cancel_mot = fields.Selection([('0','Sin Cancelar'),('1','No Quiso'),('2','Negocio cerrado'),('3','Pospone fecha'),('4','Cliente sin dinero'),('5','No tengo producto'),('6','Recuperación cobranza'),('7','No visitado')], string="Motivo Cancelacion", default="0")


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('route.order') or 'New'
        return super(RouteOrder, self).create(vals)

