import time
import pdb
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from odoo.tools import config
from odoo.addons.analytic_structure.MetaAnalytic import MetaAnalytic


class AccountAccount(models.Model):
	_inherit = 'account.account'
	_rec_name = 'code'

	nd_ids = fields.Many2many('analytic.dimension','analytic_dimension_account_rel','account_id','nd_id','Related Dimension')	
	
	def get_structures(self):		
		"""Return the browse records of every analytic structure entry associated with the account_move_line """
		ans_ids = self.env['analytic.structure'].search([('model_name', '=', 'account_move_line')])
		return ans_ids

	@api.one
	def get_dimensions(self):
		"""Return a dictionary that contains the identifier (keys) and ordering	number (values) of the analytic dimensions linked to the given Account."""
		dimensions = self.nd_ids.ids
		return {
		    ans.nd_id.id: ans.ordering for ans in self.get_structures() if ans.nd_id.id in dimensions
		}
			
	@api.one
	def get_dimensions_names(self):			
		"""Return a dictionary that contains the ordering numbers (keys) and names (values) of the analytic dimensions linked to the given Account."""
		dimensions = self.nd_ids.ids	
		return {
		    ans.ordering: ans.nd_id.name for ans in self.get_structures() if ans.nd_id.id in dimensions
		}


class AnalyticDimension(models.Model):
	_inherit = 'analytic.dimension'	
	account_ids = fields.Many2many('account.account','analytic_dimension_account_rel','nd_id','account_id',"Related Accounts")


class auto_dimensions_entry(models.Model):
	_name = 'auto.dimensions.entry'	

	def format_field_name(self, ordering, prefix='a', suffix='id'):
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)

	@api.one
	@api.depends('dimension_id')
	def _get_dst_col(self):
		dst_field_id = False
		
		if self.dimension_id:
			an_structure = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',self.dimension_id.id)])
			dst_field_name = self.format_field_name(an_structure.ordering, 'a', 'id')
			
			move_line_model = self.env['ir.model'].search([('model','=','account.move.line')]).id
			dst_field_id = self.env['ir.model.fields'].search([('model_id','=',move_line_model),('name','=',dst_field_name)]).id
		self.dst_col = dst_field_id

	sequence = fields.Integer("Sequence",default=1,required=True)
	model_id = fields.Many2one('ir.model','Model',required=True)	
	src_col = fields.Many2one('ir.model.fields','Source Field',required=True)
	dimension_id = fields.Many2one('analytic.dimension',required=True)
	dst_col = fields.Many2one('ir.model.fields','Destination Field',compute='_get_dst_col',store=True)	
	src_fnc = fields.Text("Source Function")
	active = fields.Boolean("Active",default=True)

		

