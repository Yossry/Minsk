# -*- coding: utf-8 -*-
from odoo import http

# class Mono(http.Controller):
#     @http.route('/mono/mono/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mono/mono/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mono.listing', {
#             'root': '/mono/mono',
#             'objects': http.request.env['mono.mono'].search([]),
#         })

#     @http.route('/mono/mono/objects/<model("mono.mono"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mono.object', {
#             'object': obj
#         })