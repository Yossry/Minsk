# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceReportc(http.Controller):
#     @http.route('/invoice_reportc/invoice_reportc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_reportc/invoice_reportc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_reportc.listing', {
#             'root': '/invoice_reportc/invoice_reportc',
#             'objects': http.request.env['invoice_reportc.invoice_reportc'].search([]),
#         })

#     @http.route('/invoice_reportc/invoice_reportc/objects/<model("invoice_reportc.invoice_reportc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_reportc.object', {
#             'object': obj
#         })