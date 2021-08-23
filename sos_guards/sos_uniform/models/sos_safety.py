import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

import time
import itertools
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

class sos_safety_demand(models.Model):		
	_name = "sos.safety.demand"
	_description = "Safety Demand"
	_inherit = ['mail.thread']
	_order = "date desc"
	_track = {
	}
	
	@api.one
	@api.depends('move_id','state')
	def _compute_dispatch(self):
		lines = self.env['stock.move'].search([('safety_demand_id', '=', self.id)])
		self.dispatch_ids = lines.sorted()
		
	
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]})
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]})
	name = fields.Char(string='Demand Number', readonly=True,size=16)
	employee_id = fields.Many2one('hr.employee', string = "Requested By", domain=[('is_guard','=',False),('active','=',True)], required=True, index= True, readonly=True, states={'draft': [('readonly', False)]})

	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('open','RM'),('review','Coordinator'),('approve','HOC'),('adm','Admin'),('dispatch','Store'),('done','Delivered'),('reject','Reject'),('cancel','Cancel'),], string='Status', index=True, readonly=True, default='draft',track_visibility='always', copy=False,)
	remarks = fields.Text(string='Remarks', track_visibility='onchange', readonly=False, states={'done': [('readonly', True)],'reject': [('readonly', True)]})

	uniform_demand_line = fields.One2many('sos.uniform.demand.line', 'safety_demand_id', string='Demand Lines')
	uniform_dispatch_line = fields.One2many('sos.uniform.dispatch.line', 'safety_demand_id', string='Dispatch Lines', readonly=True, states={'review': [('readonly', False)],'approve': [('readonly', False)]})
	
	move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True,)
	#dispatch_ids = fields.Many2many('stock.move', string='Dispatch Moves', compute='_compute_dispatch_lines') 
	dm_type = fields.Selection([('new_deployment','New Deployment'),('complain','Complain'),('additional_guard','Additional Guard'),('replacement','Replacement')], string='Type')	
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.safety.demand')
		vals.update({
			'name': st_number,
		})
		return super(sos_safety_demand, self).create(vals)
		
	
	@api.multi
	def demand_open(self):
		context = self._context or {}	
		for demand in self:
			demand.write({'state':'open'})
	
	@api.multi	
	def demand_review(self):
		context = self._context or {}	
		for demand in self:		
			demand.write({'state':'review'})
	
	@api.multi
	def demand_approve(self):
		context = self._context or {}	
		for demand in self:	
			demand.write({'state':'approve'})
		
	@api.multi
	def demand_admin(self):
		for demand in self:
			demand.sudo().write({'state':'adm'})	
	
	
	@api.multi
	def demand_dispatch(self):
		stock_move = self.env['stock.move']
		context = self._context or {}

		for demand in self:
			dispatch_date = demand.date			#demand.date < '2014-04-10' and demand.date or time.strftime('%Y-%m-%d')
			period_ids = self.env['sos.period'].find(dispatch_date)
			period_id = period_ids and period_ids[0] or False

			if not demand.uniform_dispatch_line:
				raise Warning(_('Please Enter the Dispatch Items.'))

			for item in demand.uniform_dispatch_line:
				vals = {
					'date': dispatch_date,
					'origin': demand.name,
					'product_uom_qty': item.product_qty,
					'product_uom': item.product_uom.id,
					'price_unit': item.product_id.list_price,

					'location_id': 12,
					'location_dest_id': demand.center_id.stock_location_id.id,

					'partner_id': 1,
					'state': 'draft',
					'warehouse_id': 1,

					'name': demand.name + ": " + item.product_id.name,
					'product_id': item.product_id.id,
				}				
				stock_move_id = stock_move.create(vals) 
				stock_move_id._action_done()
				
			demand.write({'state':'dispatch'})
		return True
	
	@api.multi
	def demand_deliver(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'done'})
	

	@api.multi	
	def demand_reject(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'reject'})
			
	
	@api.multi
	def demand_required_item_dispatch(self):
		for demand in self:
			if not demand.uniform_dispatch_line:
				for line in demand.uniform_demand_line:
					vals = {
						'product_id' : line.item_id.product_id.id,
						'product_uom' : 1,
						'product_qty' : line.approved_qty,
						'safety_demand_id' : demand.id,
						}
					dispatch_line = self.env['sos.uniform.dispatch.line'].create(vals)	
			else:
				raise Warning(_('Dispatched Items Already Entered.'))		
		

class sos_uniform_demand_line(models.Model):		
	_name = "sos.uniform.demand.line"
	_inherit = "sos.uniform.demand.line"
	
	safety_demand_id = fields.Many2one('sos.safety.demand', string='Safety Demand', index=True)
	
class sos_uniform_dispatch_line(models.Model):		
	_name = "sos.uniform.dispatch.line"
	_inherit = "sos.uniform.dispatch.line"
	
	safety_demand_id = fields.Many2one('sos.safety.demand', string='Safety Demand', index=True)
	
	
