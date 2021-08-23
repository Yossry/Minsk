# -*- coding: utf-8 -*-
from odoo import http

# class Reportemono(http.Controller):
#     @http.route('/reportemono/reportemono/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reportemono/reportemono/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reportemono.listing', {
#             'root': '/reportemono/reportemono',
#             'objects': http.request.env['reportemono.reportemono'].search([]),
#         })

#     @http.route('/reportemono/reportemono/objects/<model("reportemono.reportemono"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reportemono.object', {
#             'object': obj
#         })