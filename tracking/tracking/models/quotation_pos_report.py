# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, date

class QuotationPosReport(models.Model):
	_name = "quotation.pos.report"
	_description = "Reporte de carga"

	name = fields.Char(string='Nombre', default="/")
	state = fields.Selection([('draft','Borrador'),('validate','Validado')], string="Estado", default="draft")
	employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
	date = fields.Date(string='Fecha de pedidos', default=date.today(), required=True)
	pos_quotation_report_line = fields.One2many('pos.quotation.report.line','quotation_pos_report_id')
	pos_quotation_report_products = fields.One2many('pos.quotation.report.product','quotation_pos_report_id')

	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].get('quotation.pos.report') or '/'
		vals['name'] = seq
		return super(QuotationPosReport, self).create(vals)

	@api.multi
	def action_validate(self):
		self.state = 'validate'

	@api.multi
	def action_process(self):
		self.pos_quotation_report_line = [(5, 0, 0)]
		self.pos_quotation_report_products = [(5, 0, 0)]
		quot_ids = self.env['pos.quotation'].search([('delivery_date', '>=', self.date.strftime("%Y-%m-%d 00:00:00")),('delivery_date', '<=', self.date.strftime("%Y-%m-%d 23:59:59")),('is_lx_delivery','=',True),('employee_id','=',self.employee_id.id)])
		if quot_ids:
			for x in quot_ids:
				self.pos_quotation_report_line.create({
					'quotation_id': x.id,
					'quotation_pos_report_id': self.id,
				})
			for x in self.pos_quotation_report_line:
				for p in x.quotation_id.line_ids:
					if p.is_product_promo != True:
						p_exists = False
						for o in self.pos_quotation_report_products:
							if p.product_id.id == o.product_id.id:
								p_exists = True
								o.qty += p.qty
						if p_exists == False:
							self.pos_quotation_report_products.create({
								'product_id': p.product_id.id,
								'qty': p.qty,
								'quotation_pos_report_id': self.id,
							})
		else:
			print("NO HAY ORDENES")

class PosQuotationReportLine(models.Model):
	_name = 'pos.quotation.report.line'

	quotation_id = fields.Many2one('pos.quotation')
	quotation_pos_report_id = fields.Many2one('quotation.pos.report')

class PosQuotationReportProducts(models.Model):
	_name = 'pos.quotation.report.product'

	product_id = fields.Many2one('product.product',string="Producto")
	qty = fields.Float(string="Cantidad")
	quotation_pos_report_id = fields.Many2one('quotation.pos.report')
		