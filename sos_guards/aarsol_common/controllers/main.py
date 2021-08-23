# -*- coding: utf-8 -*-

import json
from odoo.http import Controller, route, request


class ReportController(Controller):
		
	@route([
		'/zebra/report/<converter>/<reportname>',
		'/zebra/report/<converter>/<reportname>/<docids>',
	], type='json')
	def report_routes_cusrome(self, reportname, docids=None, **data):
		context = dict(request.env.context)
		if docids:
			docids = [int(i) for i in docids.split(',')]
		if data.get('options'):
			data.update(json.loads(data.pop('options')))
		if data.get('context'):
			data['context'] = json.loads(data['context'])
			if data['context'].get('lang'):
				del data['context']['lang']
			context.update(data['context'])
		data = []
		if reportname == 'label_zebra_printer.report_zebra_shipmentlabel':
			for picking in request.env['stock.picking'].browse(docids):
				data.append({
					'label': picking.name,
				})
		if reportname == 'dokkan_ext.report_orderlabel':
			for picking in request.env['sale.order'].browse(docids).mapped('picking_ids'):
				data.append({
					'label': picking.name,
					'ordername': picking.origin,
					'picker': picking.sale_id.picker_id.name,
					'shipper': picking.sale_id.carrier_id.name,
					'items': picking.sale_id.products_count,
				})
		elif reportname == 'stock.report_location_barcode':
			for location in request.env['stock.location'].browse(docids):
				data.append({
					'name': location.name,
					'barcode': location.barcode,
				})
		#elif reportname == 'product.report_product_template_label':
		elif reportname == 'product.report_producttemplatelabel':
			for product in request.env['product.template'].browse(docids):
				                
				data.append({
					'name': product.name,
					'barcode': product.barcode or product.default_code or product.oc_sku,
					'price': product.list_price,                    
				})
		#elif reportname == 'product.report_product_label':
		elif reportname == 'product.report_productlabel':
			for product in request.env['product.product'].browse(docids):
				vars = ''
				for var in product.attribute_value_ids:
					vars += (var.attribute_id.name + ': ' + var.name)
				
				data.append({
					'name': product.name,
					'barcode': product.barcode or product.default_code or product.oc_sku,
					'price': product.list_price,
					'variants': vars,
				})

		return {'data': data}
