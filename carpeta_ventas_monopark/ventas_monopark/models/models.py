# -*- coding: utf-8 -*-
import base64
from datetime import datetime, date
from itertools import groupby
import requests
from xml.etree import ElementTree

from lxml import etree
from lxml.objectify import fromstring
from suds.client import Client
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import html_escape
from odoo.exceptions import UserError, ValidationError
#MODELO PARA FACTURAS CONCILIADAS AL PAGO
class pagos_pagos(models.Model):
	_inherit = 'account.payment'

	@api.model
	def l10n_mx_edi_get_pago_etree(self, cfdi):
		if not hasattr(cfdi, 'Complemento'):
			return None
		attribute = 'pago10:Pagos[1]'
		namespace = {'pago10': 'http://www.sat.gob.mx/Pagos'}
		node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
		return node[0] if node else None


	@api.multi
	def complemento(self):
		self.pagos_con = [(5, 0, 0)]
		data = base64.decodestring(self.l10n_mx_edi_cfdi)
		root =ElementTree.fromstring(data)
		#print ("roooooooooooooooooooooooooooot",root)
		count = 0
		lista = []
		cont = 0
		if count == 0:
			count += count + 1
			for child in root.findall('{http://www.sat.gob.mx/cfd/3}Complemento'):
				for pagos in child:
					for pago in pagos:
						for doc in pago:
							if lista:
								for i in lista:
									if i['folio'] != doc.attrib['Folio']:
										vals = {
											'folio': doc.attrib['Folio'],
											'id_documento':doc.attrib['IdDocumento'],
											'no_parc':doc.attrib['NumParcialidad'],
											'metodo_de_pago_dr': doc.attrib['MetodoDePagoDR'],
											'moneda':doc.attrib['MonedaDR'],
											'saldo_anterior':doc.attrib['ImpSaldoAnt'],
											'pagado':doc.attrib['ImpPagado'],
											'saldo_insoluto':doc.attrib['ImpSaldoInsoluto'],
											'acc_payment':self.id
										}
										lista.append(vals)
							else:
								if cont == 0:
									vals = {
										'folio': doc.attrib['Folio'],
										'id_documento':doc.attrib['IdDocumento'],
										'no_parc':doc.attrib['NumParcialidad'],
										'metodo_de_pago_dr': doc.attrib['MetodoDePagoDR'],
										'moneda':doc.attrib['MonedaDR'],
										'saldo_anterior':doc.attrib['ImpSaldoAnt'],
										'pagado':doc.attrib['ImpPagado'],
										'saldo_insoluto':doc.attrib['ImpSaldoInsoluto'],
										'acc_payment':self.id
									}
									lista.append(vals)
									cont = 1
		return lista

		self.pagos_con.create(lista)
#MODELO PARA LOS TIEMPOS DE ENTREGA EN EL MODELO DE VENTAS
class TiempoEntrega(models.Model):
	_name = "tiempo.entrega"

	name = fields.Char(string="Nombre")
	description = fields.Char(string="Descripción")
	cedis_selection = fields.Selection([('occidente','Cedis Occidente'),('centro','Cedis Centro'),('sur','Cedis Sur')],string='Cedis')
	
#MODELOS PARA LAS OBSERVACIONES EN EL MODELO DE VENTAS
class Observaciones(models.Model):
	_name = "obser.sale"

	name = fields.Char(string="Nombre")
	description = fields.Text(string="Descripción de la observación")

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			record_name = str(record.name)
			result.append((record.id, record_name))
		return result

#INHERIT EN EL MODELO DE VENTAS, PARA AGREGAR NUEVOS CAMPOS AL MODELO
class ReportCot(models.Model):
	_inherit = "sale.order"
	
	proyecto_sale_dos = fields.Char(string="Proyecto", compute="_opportunity_in_proyecto")
	cargo_envio = fields.Selection(selection=[
		('type1', 'Envio por cobrar'),
		('type2', 'Flete contrado'),
		('type3', 'Por parte del cliente'),
		('type4', 'Por confirmar'),
		('type5', 'Otros'),
		('type6', 'Gratis ZMG'),
		('type7', 'Gratis ZMCDMX'),
		('type8', 'Gratis ZMMERIDA'),], string="Cargo de envio", default='type1')
	instalacion = fields.Selection(selection=[
		('type1', 'Por parte del cliente'),
		('type2', 'Cotizado'),
		('type3', 'Por confirmar'),
		('type4', 'Otros'),
		('type6', 'Gratis ZM GDL'),
		('type7', 'Gratis ZM CDMX'),
		('type8', 'Gratis ZM Mérida'),], string="Instalación", default='type1')
	entrega = fields.Many2many('tiempo.entrega', string="Tiempo de entrega")
	forma_pago = fields.Char(string="Forma de pago")
	observaciones =fields.Many2many('obser.sale', string="Observaciones")
	pago_importacion = fields.Char(string="En los productos de importacion y fabricacion el pago sera")
	nota_venta = fields.Char(string="Nota", default="Precios sujetos a cambio sin previo aviso")
	comentarios = fields.Char(string="Comentarios")
	proyecto = fields.Char(string="Proyecto")
	aditional_comment = fields.Text(string="Comentarios adicionales")

	@api.one
	def _opportunity_in_proyecto(self):
		for record in self:
			if record.opportunity_id:
				record.proyecto_sale_dos = record.opportunity_id.name
			else:
				record.proyecto_sale_dos = ""	

#INHERIT A LA TABLA DE PEDIDO DE VENTA, PARA AGREGAR DOS NUEVAS COLUMNAS
class ReportCot(models.Model):
	_inherit = "sale.order.line"

	#price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
	imagen_producto = fields.Binary(compute="_get_imagen")
	tiempo_entrega_tabla = fields.Many2many('tiempo.entrega', string="Tiempo de entrega")
	price_product_cantidad = fields.Monetary(compute='_compute_product_cantidad', string='Subtotal', readonly=True, store=True)
	precio_especial= fields.Monetary(string="Precio especial", compute="_get_precio_especial")
	precio_publico_reporte = fields.Monetary(compute="_get_precio_publico_reporte")
	precio_distribuidor_reporte = fields.Monetary(compute="_get_precio_distribuidor_reporte")
	
	@api.depends('price_unit')
	def _get_precio_especial(self):
		for line in self:
			precio = 0.0
			if line.discount:
				precio = line.price_unit - (line.price_unit * (line.discount / 100))
				line.precio_especial = precio
			else:
				line.precio_especial = 0.0

	@api.depends('product_id.lst_price')
	def _get_precio_publico_reporte(self):
		for line in self:
			precio = 0.0
			if line.product_id:
				precio = line.product_id.lst_price
				line.precio_publico_reporte = precio
			else:
				line.precio_publico_reporte = 0.0
	@api.depends('price_unit')
	def _get_precio_distribuidor_reporte(self):
		for line in self:
			precio = 0.0
			if line.price_unit:
				precio = line.price_unit
				line.precio_distribuidor_reporte = precio
			else:
				line.precio_distribuidor_reporte = 0.0							

	@api.depends('price_unit', 'product_uom_qty')
	def _compute_product_cantidad(self):
		for line in self:
			line.price_product_cantidad = line.product_uom_qty * line.price_unit

	@api.depends('product_id')
	def _get_imagen(self):
		for line in self:
			if line.product_id:
				line.imagen_producto = line.product_id.image_medium

class PrickingStock(models.Model):
	_inherit = "stock.picking"

	state = fields.Selection([
        ('draft', 'BORRADOR'),
        ('waiting', 'ESPERANDO OTRA OPERACIÓN'),
        ('confirmed', 'EN ESPERA'),
        ('assigned', 'RESERVADO'),
        ('done', 'HECHO'),
        ('cancel', 'CANCELADO'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

class StockMoveInherit(models.Model):
	_inherit = "stock.move"

	tiempo_entrega_tabla = fields.Many2many('tiempo.entrega', string="Tiempo de entrega", related="sale_line_id.tiempo_entrega_tabla")

class checkbox(models.Model):
	_inherit="product.pricelist"

	tipotarifa=fields.Boolean(string="¿Es tarifa publica?")