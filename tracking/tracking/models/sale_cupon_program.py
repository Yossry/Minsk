# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval

class SaleCouponReward(models.Model):
	_inherit = 'sale.coupon.reward'
	discount_type = fields.Selection([('percentage', 'Percentage'),('fixed_amount', 'Fixed Amount')], default="fixed_amount",help="Percentage - Entered percentage discount will be provided\n" + "Amount - Entered fixed amount discount will be provided")

class SaleCuponProgram(models.Model):
	_inherit = 'sale.coupon.program'

	@api.multi
	def get_domain_products_ids(self):
		domain = safe_eval(self.rule_products_domain)
		print("DOMINIO: ",domain)
		products= self.env['product.product'].search(domain)
		lista = []
		for x in products:
			if x.default_code:
				lista.append(x.default_code)
		
		return lista

	@api.multi
	def get_domain_partners_ids(self):
		domain = False
		if self.rule_partners_domain:
			domain = safe_eval(self.rule_partners_domain)
		else:
			domain = []
		print("DOMINIO: ",domain)
		lista = []
		if domain == []:
			return lista
		else:
			partners= self.env['res.partner'].search(domain)
			if partners:
				for x in partners:
					if x.customer == True:
						lista.append(str(x.id))
			
			return lista
	#products_dom = fields.Many2many("product.product", string="Productos")