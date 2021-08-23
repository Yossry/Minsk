# -*- coding: utf-8 -*-
# Copyright 2019, XMARTS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api

class PosQuotationLX(models.Model):
	_inherit = 'pos.quotation'

	is_lx_delivery = fields.Boolean(
	    string='Entrega de LXTRACK',
	    default=False
	)
	delivery_date = fields.Datetime(
	    string='Fecha Entrega',
	)
	sync_lx = fields.Boolean(
	    string='Sincronizado con LXTRACK ?',
	    default=False
	)
	employee_id = fields.Many2one('hr.employee',string="Encargado", related="partner_id.zona2.user_id")
	partner_shipping_id = fields.Many2one('res.partner',string='Direccion de entrega')



class PosQuotationLine(models.Model):
	_inherit = 'pos.quotation.line'

	is_product_promo = fields.Boolean(
		string='Es Promocion?',
		default=False
	)