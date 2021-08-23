# -*- coding: utf-8 -*-
from odoo import http

# class WizaCon(http.Controller):
#     @http.route('/wiza_con/wiza_con/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wiza_con/wiza_con/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wiza_con.listing', {
#             'root': '/wiza_con/wiza_con',
#             'objects': http.request.env['wiza_con.wiza_con'].search([]),
#         })

#     @http.route('/wiza_con/wiza_con/objects/<model("wiza_con.wiza_con"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wiza_con.object', {
#             'object': obj
#         })