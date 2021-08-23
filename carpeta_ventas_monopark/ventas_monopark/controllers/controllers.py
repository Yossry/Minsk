# -*- coding: utf-8 -*-
from odoo import http

# class VentasMonopark(http.Controller):
#     @http.route('/ventas_monopark/ventas_monopark/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ventas_monopark/ventas_monopark/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ventas_monopark.listing', {
#             'root': '/ventas_monopark/ventas_monopark',
#             'objects': http.request.env['ventas_monopark.ventas_monopark'].search([]),
#         })

#     @http.route('/ventas_monopark/ventas_monopark/objects/<model("ventas_monopark.ventas_monopark"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ventas_monopark.object', {
#             'object': obj
#         })