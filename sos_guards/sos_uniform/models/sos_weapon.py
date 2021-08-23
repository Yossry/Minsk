import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

import time
import itertools
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import  Warning, RedirectWarning, UserError
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class sos_weapon_demand(models.Model):		
	_name = "sos.weapon.demand"
	_description = "SOS Weapons"
	_inherit = ['mail.thread']
	_order = "date desc"

	@api.one
	@api.depends('move_id','state')
	def _compute_dispatch(self):
		lines = self.env['stock.move'].search([('weapon_demand_id', '=', self.id)])
		self.dispatch_ids = lines.sorted()
		
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]})
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]})
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
	employee_id = fields.Many2one('hr.employee', string = "Requested By", domain=[('active','=',True)], required=True, index= True, readonly=True, states={'draft': [('readonly', False)]})
	name = fields.Char(string='Demand Number', readonly=True,size=16)
		
	is_new_post = fields.Boolean(string='Is New Post', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
	reason = fields.Selection([('fire test','Fire Test'),('misfire','Misfie'),('faulty','Faulty'),('new deployment','New Deployment'),('additional guard','Additional Guard'),('replacement','Replacement'),('shortage','Shortage'),('weapon change','Weapon Change')], string='Demand Reason',copy=False,)
	
	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('open','RM'),('review','Coordinator'),('approve','HOC'),('adm','Admin'),('dispatch','Store'),('done','Delivered'),('reject','Reject'),('cancel','Cancel'),], string='Status', index=True, readonly=True, default='draft',track_visibility='always', copy=False,)
	remarks = fields.Text(string='Remarks', track_visibility='onchange', readonly=False, states={'done': [('readonly', True)],'reject': [('readonly', True)]})
	
	weapon_demand_line = fields.One2many('sos.weapon.demand.line', 'weapon_demand_id', string='Demand Lines')
	weapon_dispatch_line = fields.One2many('sos.weapon.dispatch.line', 'weapon_demand_id', string='Dispatch Lines', readonly=True, states={'review': [('readonly', False)],'approve': [('readonly', False)]})
	move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True,)
	dispatch_ids = fields.Many2many('stock.move', string='Dispatch Moves', compute='_compute_dispatch') 
	dispatch_date = fields.Date('Dispatch Date',readonly=True)
	dm_type = fields.Selection([('new_deployment','New Deployment'),('complain','Complain'),('additional_guard','Additional Guard'),('replacement','Replacement')], string='Type')	
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.weapon.demand')
		vals.update({
			'name': st_number,
		})		
		return super(sos_weapon_demand, self).create(vals)

	@api.multi
	def write(self,vals):
		obj_seq = self.env['ir.sequence']
		context = self._context or {}
		for rec in self:
			if not rec.name:
				st_number = obj_seq.next_by_code('sos.weapon.demand')
				vals.update({
					'name': st_number,
				})	
		return super(sos_weapon_demand, self).write(vals)
	
	@api.multi
	def demand_open(self):
		for demand in self:		
			demand.write({'state':'open'})
	
	@api.multi
	def demand_review(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'review'})

	@api.multi
	def demand_approve(self):
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
			
			if not demand.weapon_dispatch_line:
				raise Warning(_('Please Enter the Dispatch Items.'))
			
			for item in demand.weapon_dispatch_line:
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
					'weapon_demand_id': demand.id,
				}				
				stock_move_id = stock_move.create(vals) 
				stock_move_id._action_done()
			demand.write({'state':'dispatch','dispatch_date':dispatch_date})
		return True

	@api.multi
	def demand_delivered(self):
		stock_move = self.env['stock.move']
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']
		context = self._context or {}
		
		for demand in self:
			dispatch_date = demand.date			#demand.date < '2014-04-10' and demand.date or time.strftime('%Y-%m-%d')
			period_ids = self.env['sos.period'].sudo().find(dispatch_date)
			period_id = period_ids and period_ids[0] or False	
			amount = 0	
			
			for item in demand.weapon_demand_line:
				if item.action == 'safety':
					act = 'Safety'
				else:
					act = 'Dispatch'

				for product in item.item_id.product_ids:
					vals = {
						'date': dispatch_date,
						'origin': demand.name + ": " + act,
						'product_uom_qty': item.qty,
						'product_uom': product.uom_id.id,

						'location_id': demand.center_id.stock_location_id.id,
						#'location_dest_id': 25,
						'location_dest_id': 9,

						'partner_id': 1,
						'state': 'draft',
						'warehouse_id': 1,
						'invoice_state': 'none',

						'name': demand.name + ":" + act[0] + ":" + product.name,
						'product_id': product.id,	
						'post_id': demand.post_id.id,
						'weapon_demand_id': demand.id,
					}
					stock_move_id = stock_move.create(vals) 
					stock_move_id._action_done()
					amount += item.qty * product.list_price
					
			#MOVE
			move = {
				'ref': demand.name,
				'name': demand.name,
				'journal_id': 9,  # Stock Journal
				'date': dispatch_date,
				'post_id': demand.post_id.id,
				'narration': demand.name + ":Regular:" + str(demand.date),
			}														
			move_id = move_obj.sudo().create(move)	
			
			#DEBIT LINE
			move_line = {
				'name': demand.name,
				'move_id': move_id.id,
				'debit': amount,
				'credit': 0.0,
				'account_id': 140, # Ammunition Exp 41011					
				'journal_id': 9,  # Stock Journal
				'date': dispatch_date,
				'post_id': demand.post_id.id,
			}
			move_line_obj.sudo().create(move_line)
			
			#CREDIT LINE
			move_line = {
				'name': demand.name,
				'move_id': move_id.id,
				'debit': 0.0,
				'credit': amount,
				'account_id': 50, # Uniform Asset  10203					
				'journal_id': 9,  # Stock Journal
				'date': dispatch_date,
				'post_id': demand.post_id.id,
			}		
			
			move_line_obj.sudo().create(move_line)
			move_id.state ='posted'
			demand.write({'state':'done','move_id':move_id.id})
		return True
	
	@api.multi
	def demand_required_item_dispatch(self):
		for demand in self:	
			#pdb.set_trace()
			if not demand.weapon_dispatch_line:
				for line in demand.weapon_demand_line:
					prd = False
					if line.item_id.product_ids:
						prd = line.item_id.product_ids[0]
					if prd:	
						vals = {
							'product_id' : prd.id,
							'product_qty' : line.qty,
							'weapon_demand_id' : demand.id,
							'product_uom' : prd.uom_id and prd.uom_id.id or False,
							}
						dispatch_line = self.env['sos.weapon.dispatch.line'].create(vals)	
			else:
				raise Warning(_('Dispatched Items Already Entered.'))

	@api.multi
	def demand_reject(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'reject'})


class sos_weapon_items(models.Model):		
	_name = "sos.weapon.items"
	_description = "Weapon Items"
	
	name = fields.Char('Item Name')
	req_size = fields.Boolean(string='Size Required?')
	product_ids = fields.Many2many('product.product','sos_weapon_product', 'item_id', 'product_id', string='Items')


class sos_weapon_demand_line(models.Model):		
	_name = "sos.weapon.demand.line"
	_description = "SOS Weapons Line"
	
	item_id = fields.Many2one('sos.weapon.items',string='Item')
	qty = fields.Integer(string='Qty',default=1,)
	req_size = fields.Boolean(string='Size Required?')
	size = fields.Char(string='Size')
	action = fields.Selection([('safety','Use Safety Stock'),('dispatch','Dispatch')], string='Action', default='dispatch', copy=False,) 
	weapon_demand_id = fields.Many2one('sos.weapon.demand', string='Weapon Lines', index=True)
	date = fields.Date(string='Last Inssuance' ,required=False)
	
	@api.onchange('item_id')
	def onchange_item_id(self):
		context = self._context or {}
		res = {'value': {'req_size': False}}
		if not self.item_id:
			return res

		item = self.env['sos.weapon.items'].search([('id', '=', self.item_id.id)])			
		res['value'].update({'req_size': item.req_size})
		return res

	@api.one	
	def unlink(self):
		if self.weapon_demand_id.state != 'draft':
			raise UserError('You can delete the Entry whose demand is in the in Draft State.')
		ret = super(sos_weapon_demand_line, self).unlink()
		return ret		


class sos_weapon_dispatch_line(models.Model):		
	_name = "sos.weapon.dispatch.line"
	_description = "Weapon Dispatch Line"
	
	def _get_uom_id(self):
		try:
			proxy = self.env['ir.model.data']
			result = proxy.get_object_reference('product', 'product_uom_unit')
			return result[1]
		except Exception:
			return False

	product_id = fields.Many2one('product.product',string='Product')
	product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)
	stock_qty = fields.Float(string='Stock Qty')
	product_qty = fields.Integer(string='Qty',default=1,)
	weapon_demand_id = fields.Many2one('sos.weapon.demand', string='Lines', index=True)

	@api.onchange('product_id')
	def onchange_product_id(self):
		context = self._context or {}
		res = {'value': {'price_unit': 0.0}}
		if not self.product_id:
			return res
		product = self.env['product.product'].search([('id', '=', self.product_id.id)])
		# - set a domain on product_uom
		res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
		uom_id = product.uom_id.id
		res['value'].update({'product_uom': uom_id})
		stock_qty = product.qty_available
		res['value'].update({'stock_qty': stock_qty})
		return res