import time
import pdb
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _

from odoo.tools import config
from odoo.addons.analytic_structure.MetaAnalytic import MetaAnalytic
import math


class AccountDimensionEntry(models.TransientModel):
	_name = "account.dimension.entry"
					
	@api.multi
	@api.depends('d_bin')
	def _get_d_bin(self):
		if self.d_bin:
			self.H10_id = int(self.d_bin[0:1])
			self.H9_id = int(self.d_bin[1:2])
			self.H8_id = int(self.d_bin[2:3])
			self.H7_id = int(self.d_bin[3:4])
			self.H6_id = int(self.d_bin[4:5])
			self.H5_id = int(self.d_bin[5:6])
			self.H4_id = int(self.d_bin[6:7])
			self.H3_id = int(self.d_bin[7:8])
			self.H2_id = int(self.d_bin[8:9])
			self.H1_id = int(self.d_bin[9:10])

	model_name = fields.Char()
	model_db_name = fields.Char()
	rec_id = fields.Integer()
	readonly = fields.Boolean()
	account_id = fields.Many2one('account.account','Account')
	d_bin = fields.Char("Binary Dimension")

	a1_id = fields.Many2one('analytic.code')  # ,'Cost Center',domain=[('nd_id', '=', 1)]
	a2_id = fields.Many2one('analytic.code')
	a3_id = fields.Many2one('analytic.code')
	a4_id = fields.Many2one('analytic.code')
	a5_id = fields.Many2one('analytic.code')
	a6_id = fields.Many2one('analytic.code')
	a7_id = fields.Many2one('analytic.code')
	a8_id = fields.Many2one('analytic.code')
	a9_id = fields.Many2one('analytic.code')
	a10_id = fields.Many2one('analytic.code')
	
	H1_id = fields.Integer(compute='_get_d_bin')
	H2_id = fields.Integer(compute='_get_d_bin')
	H3_id = fields.Integer(compute='_get_d_bin')
	H4_id = fields.Integer(compute='_get_d_bin')
	H5_id = fields.Integer(compute='_get_d_bin')
	H6_id = fields.Integer(compute='_get_d_bin')
	H7_id = fields.Integer(compute='_get_d_bin')
	H8_id = fields.Integer(compute='_get_d_bin')
	H9_id = fields.Integer(compute='_get_d_bin')
	H10_id = fields.Integer(compute='_get_d_bin')	

	@api.model
	def fields_get(self, allfields=None, attributes=None):
		model_db_name = self._context.get('default_model_db_name',False)
		
		res = super(AccountDimensionEntry, self).fields_get(allfields=allfields, attributes=attributes)
		analytic_osv = self.env['analytic.structure']
		if model_db_name:			
			res = analytic_osv.analytic_fields_with_domains_get(model_db_name, res, 'a', 'id')		
		return res	
	
	def format_field_name(self, ordering, prefix='a', suffix='id'):		
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)
	
	@api.onchange('account_id')
	def _onchange_account_id(self):		
		if self.account_id:			
			dimensions = self.account_id.nd_ids						
			structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids),('model_name','=',self.model_db_name)])
			used = [int(structure.ordering) for structure in structures]
			if self.model_name and self.rec_id:
				rec = self.env[self.model_name].browse(self.rec_id)[0]
									
			number = 0
			size = int(config.get_misc('analytic', 'analytic_size', 10))
			for n in range(1, size + 1):				
				if n in used:
					if self.model_name and self.rec_id:
						
						src = self.format_field_name(n,'a','id')	
						self[src] = rec[src]
					src_data = 1
					number += math.pow(2,n-1)
			self.d_bin = bin(int(number))[2:].zfill(10)
			
	def save_dimensions(self):
		if self.model_name and self.rec_id:
			rec = self.env[self.model_name].browse(self.rec_id)[0]
			size = int(config.get_misc('analytic', 'analytic_size', 10))
			for n in range(1, size + 1):				
				src = self.format_field_name(n,'a','id')	
				rec[src] = self[src]