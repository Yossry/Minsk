# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class PriceListItemInherit(models.Model):
	_inherit = 'product.pricelist.item'

	price_with_ieps = fields.Float(string="Precio con IEPS", compute="_compute_amount")
	price_tax = fields.Float(string="Impuestos", compute="_compute_amount")
	price_total = fields.Float(string="Precio Final", compute="_compute_amount")
	percent_tax = fields.Integer(string="Porcentaje impuestos", compute="_compute_amount")
	ieps_taxes = fields.Many2many("account.tax", string="Impuestos IEPS", compute="_compute_amount")

	@api.depends('price_with_ieps', 'price_tax', 'price_total', 'product_tmpl_id', 'compute_price', 'fixed_price')
	def _compute_amount(self):
		for line in self:
			price = line.fixed_price
			taxs = line.product_tmpl_id.taxes_id
			lista = []
			ieps_amount = 0
			ieps_list = []
			for x in taxs:
				ieps = False
				for z in x.tag_ids:
					if z.name == 'IEPS':
						ieps = True
				if ieps == False:
					lista.append(x.id)
			for x in line.product_tmpl_id.taxes_id:
				ieps = False
				for z in x.tag_ids:
					if z.name == 'IEPS':
						ieps = True
				if ieps == True:
					ieps_amount += x.amount
					ieps_list.append(x.id)
			mytaxes = self.env['account.tax'].search([('id','in',lista)])
			print("PRECIOS ",price,ieps_amount,(price+ieps_amount),mytaxes)
			tax = 0
			p_tax = 0
			for t in mytaxes:
				tax += (price+ieps_amount)*(t.amount/100)
				p_tax += t.amount
			line.update({
				'price_tax': round(tax,2),
				'price_total': round((price + ieps_amount + tax),2),
				'price_with_ieps': round((ieps_amount),2),
				'percent_tax': p_tax,
				'ieps_taxes': [(6,0,ieps_list)],
			})

class PosOrder(models.Model):
	_inherit = 'pos.order'

	@api.multi
	def recalcula_impuestos(self):
		imp = 0 
		tot = 0
		for l in self.lines:
			imp += l.price_subtotal_incl - l.price_subtotal
			tot += l.price_subtotal_incl
		self.amount_tax = imp
		self.amount_total = tot
		return True

class SaleCuponProgram(models.Model):
	_inherit = 'sale.coupon.program'

	@api.constrains('name')
	def _check_name(self):
		rec = self.env['sale.coupon.program'].search(
		[('name', '=', self.name),('id', '!=', self.id),('program_type','=','promotion_program')])
		if rec:
			raise ValidationError(_('Ya existe una promocion con este nombre.'))