import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class sos_uniform_demand(models.Model):		
	_name = "sos.uniform.demand"
	_description = "Uniform Demand"
	_inherit = ['mail.thread']
	_order = "date desc"
	_track = {
	}
	
	@api.one
	@api.depends('move_id','state')
	def _compute_dispatch_lines(self):
		lines = self.env['stock.move'].search([('uniform_demand_id', '=', self.id)])
		self.dispatch_ids = lines.sorted()
	
	@api.one
	@api.depends('move_id')
	def _compute_move_value(self):
		self.move_value = 0
		lines = self.env['account.move.line'].search([('move_id', '=', self.move_id.id),('debit', '>', 0)])
		self.move_value = sum(line.debit for line in lines)
	
	@api.one
	@api.depends('new_guards', 'existing_guards')
	def _compute_total(self):
		self.no_of_guards = self.new_guards + self.existing_guards
	
	demand_type = fields.Selection([('safety','Use Safety Stock'),('new','New Demand from Headoffice')], string='Demand Type', default='new', copy=False,) 
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]})
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]})
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
	employee_id = fields.Many2one('hr.employee', string = "Requested By", domain=[('is_guard','=',False),('active','=',True)], required=True, index= True, readonly=True, states={'draft': [('readonly', False)]})
	name = fields.Char(string='Demand Number', readonly=True,size=16)
			
	is_new_post = fields.Boolean(string='Is New Post', default=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
	
	new_guards = fields.Integer(string='New Guards', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
	existing_guards = fields.Integer(string='Existing Guards', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
	
	no_of_guards = fields.Integer(string='Total Guards', compute='_compute_total',readonly=True)
	
	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'draft': [('readonly', True)]})
	delivery_date = fields.Date(string='Delivery Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'dispatch': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('open','RM'),('review','Coordinator'),('approve','HOC'),('adm','Admin'),('dispatch','Store'),('done','Delivered'),('reject','Reject'),('cancel','Cancel'),], string='Status', index=True, readonly=True, default='draft',track_visibility='always', copy=False,)
	remarks = fields.Text(string='Remarks', track_visibility='onchange', readonly=False, states={'done': [('readonly', True)],'reject': [('readonly', True)]})
		
	uniform_demand_line = fields.One2many('sos.uniform.demand.line', 'uniform_demand_id', string='Demand Lines', required=True)
	uniform_dispatch_line = fields.One2many('sos.uniform.dispatch.line', 'uniform_demand_id', string='Dispatch Lines', readonly=True, states={'review': [('readonly', False)],'approve': [('readonly', False)]})
	move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True,)
	move_value = fields.Integer(string='Move Value', compute='_compute_move_value',readonly=True)
	dispatch_ids = fields.Many2many('stock.move', string='Dispatch Moves', compute='_compute_dispatch_lines')
	dispatch_date = fields.Date('Dispatch Date',readonly=True,)
	
	rfid_ok = fields.Boolean(string='RFID OK', default=False)
	rfid_uniform_demand_lines = fields.One2many('sos.uniform.demand.line', 'uniform_demand_id', string='RFID Demand',domain=[('tracking','=','serial'),('rfid','=',False)])
	
	dm_type = fields.Selection([('new_deployment','New Deployment'),('complain','Complain'),('additional_guard','Additional Guard'),('replacement','Replacement')], string='Type') 
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.uniform.demand')
		vals.update({
			'name': st_number,
		})		
		return super(sos_uniform_demand, self).create(vals)
		
	@api.multi
	def write(self,vals):
		obj_seq = self.env['ir.sequence']
		context = self._context or {}
		
		for rec in self:
			if not rec.name:
				st_number = obj_seq.next_by_code('sos.uniform.demand')
				vals.update({
					'name': st_number,
				})	
		return super(sos_uniform_demand, self).write(vals)		
	
	@api.multi	
	def demand_open(self):
		for demand in self:		
			if demand.is_new_post == False and demand.demand_type == 'new':
				for line in demand.uniform_demand_line:
					if not line.guard_id:
						raise Warning(_('Please Enter the Guard Names.'))	
			
			if demand.demand_type == 'safety':
				demand.state = 'dispatch'
			else:
				demand.state = 'open'
		
	@api.multi
	def demand_review(self):
		for demand in self:
			for line in demand.uniform_demand_line:
				line.approved_qty = line.qty
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
		for demand in self:
			dispatch_date =	datetime.today().strftime('%Y-%m-%d')
			
			if not demand.uniform_dispatch_line:
				raise Warning(_('Please Enter the Dispatch Items.'))
			
			# Make the Dictionary of required items with Qty		
			req_prods = {}
			for item in demand.uniform_demand_line:
				for prod in item.item_id.product_id:
					qty = req_prods.get(prod.id,0) 
					req_prods.update({prod.id: qty+item.approved_qty})
			
			#If matching the Dispatched and required quantities	
			for item in demand.uniform_dispatch_line:
				qty = req_prods.get(item.product_id.id,0) 
				qty = qty-item.product_qty
				if qty == 0:
					req_prods.pop(item.product_id.id, None)
				else:					
					req_prods.update({item.product_id.id: qty})
					
			if req_prods:
				raise Warning(_('Approved & Dispatched Items does not match.'))
	
			for item in demand.uniform_dispatch_line:
				
				# Changing the RFID State From Main Store to Regional Office 
				for btn in item.button_pack_ids:
						button_id = self.env['sos.button.inventory'].search([('name','=',btn.rfid),('state','=','main_store')])
						if button_id:
							button_id.state= 'branch_store'
				
				# Making Dict for Stock Move entry	
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
					'uniform_demand_id': demand.id,
				}				
				stock_move_id = stock_move.create(vals) 
				stock_move_id._action_done()
								
		self.write({'state':'dispatch','dispatch_date':dispatch_date})
			
	@api.multi
	def demand_delivered(self):
		stock_move = self.env['stock.move']
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']
		
		for demand in self:
			for line in demand.uniform_demand_line:
				if not line.guard_id:
					raise Warning(_('Please Enter the Guard Names.'))		
			
			delivery_date = demand.delivery_date
					
			amount = 0			
			for item in demand.uniform_demand_line:
				if demand.demand_type == 'safety':
					act = 'Safety'
				else:
					act = 'New'
					
				for product in item.item_id.product_id:
					vals = {
						'date': delivery_date,
						'origin': demand.name + ": " + act,
						'product_uom_qty': item.qty,
						'product_uom': product.uom_id.id,

						'location_id': demand.center_id.stock_location_id.id,
						#'location_dest_id': 25,
						'location_dest_id': 9,

						'partner_id': 1,
						'state': 'draft',
						'warehouse_id': 1,

						'name': demand.name + ":" + act[0] + ":" + product.name,
						'product_id': product.id,	
						'emp_id': item.guard_id.id,
						'uniform_demand_id': demand.id,
					}
					stock_move_id = stock_move.create(vals)
					stock_move_id._action_done()
					amount += item.qty * product.list_price
					
					## Creating RFID Entry in Guard Form and Chaning the State from Main Store to Guard
					res = {
						'employee_id' : item.guard_id.id,
						'rf_id' : item.rfid,
						'state' : 'draft',
					}
				new_rec = self.env['employee.rfid'].create(res)
				button_id = self.env['sos.button.inventory'].search([('name','=',item.rfid),('state','=','branch_store')])
				if button_id:
					button_id.state='guard'
					
					
			move_lines=[]
			move_lines.append((0,0,{
				'name': demand.name,
				'debit': amount,
				'credit': 0.0,
				'account_id': 139,	 # Uniform Exp 41010				
				'journal_id': 9,  # Stock Journal			
				'date': delivery_date,
				'uniform_demand_id': demand.id,
				'post_id': demand.post_id.id,
				'a5_id' : demand.post_id.partner_id.analytic_code_id and demand.post_id.partner_id.analytic_code_id.id or False, #Post
				'a3_id' : demand.post_id.project_id.analytic_project_id and demand.post_id.project_id.analytic_project_id.id or False, #Project
				'a4_id' : demand.post_id.region_id.analytic_region_id and demand.post_id.region_id.analytic_region_id.id or False, #Region
			}))
			move_lines.append((0,0,{
				'name': demand.name,
				'debit': 0.0,
				'credit': amount,
				'account_id': 49,	 # Uniform Asset  10202				
				'journal_id': 9,  # Stock Journal			
				'date': delivery_date,
				'uniform_demand_id': demand.id,
				'post_id': demand.post_id.id,				

			}))
			move = {
				'ref': demand.name,
				'name': demand.name,
				'journal_id': 9,  # Stock Journal
				'date': delivery_date,
				'post_id': demand.post_id.id,
				'narration': demand.name + ":Regular:" + str(demand.date),
				'state': 'draft',
				'line_ids': move_lines,					
			}																
			move_id = move_obj.sudo().create(move)
			move_id.state = 'posted'		

			demand.write({'state':'done','move_id':move_id.id})

	@api.multi		
	def demand_reject(self):
		for demand in self:
			demand.write({'state':'reject'})
		
	
	@api.multi
	def demand_required_item_dispatch(self):
		for demand in self:
			if not demand.uniform_dispatch_line:
				for line in demand.uniform_demand_line:
					vals = {
						'product_id' : line.item_id.product_id.id,
						'product_uom' : line.item_id.product_id.uom_id and line.item_id.product_id.uom_id.id or False,
						#'stock_qty' : 0,
						'product_qty' : line.approved_qty,
						'uniform_demand_id' : demand.id,
						}
					dispatch_line = self.env['sos.uniform.dispatch.line'].create(vals)	
			else:
				raise Warning(_('Dispatched Items Already Entered.'))	
		

	@api.one
	def save(self):
		a = len(self.rfid_uniform_demand_lines)
		if a == 0:
			self.rfid_ok = True
			self.state='rfid'
		return {'type': 'ir.actions.act_window_close'}
	
	
	@api.multi
	def demand_rfid(self):
		context = self._context or {}
		ctx=context.copy()
		assert len(self.ids) > 0
		data_obj = self.env['ir.model.data']
		pack = self.browse(self.ids[0])
		view = data_obj.xmlid_to_res_id('sos_uniform.sos_uniform_demand_rfid_form_view')

		ctx.update({'serial': True,})
		return {
			 'name': _('RFID Demand View'),
			 'type': 'ir.actions.act_window',
			 'view_type': 'form',
			 'view_mode': 'form',
			 'res_model': 'sos.uniform.demand',
			 'views': [(view, 'form')],
			 'view_id': view,
			 'target': 'new',
			 'res_id': pack.id,
			 'context': ctx,
		}
		
		
class sos_uniform_items(models.Model):	
	_name = "sos.uniform.items"
	_description = "Uniform Items"
	
	name = fields.Char('Item Name')
	req_size = fields.Boolean(string='Size Required?')
	product_id = fields.Many2one('product.product','Item')
	active = fields.Boolean('Active', default=True)

class sos_uniform_demand_line(models.Model):		
	_name = "sos.uniform.demand.line"
	_description = "Uniform Demand Line"
	
	@api.one
	def _compute_stock_lines(self):
		related_recordset = self.env["stock.move"].search([('emp_id','=',self.guard_id.id)])
		self.stock_lines = related_recordset.ids

	item_id = fields.Many2one('sos.uniform.items',string='Item')
	qty = fields.Integer(string='Qty',default=1,)
	req_size = fields.Boolean(string='Size Required?')
	size = fields.Char(string='Size')
	guard_id = fields.Many2one('hr.employee',string='Guard',required=True)
	action = fields.Selection([('safety','Use Safety Stock'),('dispatch','Dispatch')], string='Action', default='dispatch', copy=False,) 
	uniform_demand_id = fields.Many2one('sos.uniform.demand', string='Lines', index=True)
	date = fields.Date(string='Last Inssuance' ,required=False)
	state = fields.Selection([('draft','Draft'),('open','Open'),('review','Review'),('approve','Approve'),('dispatch','Dispatch'),('done','Delivered'),('reject','Reject'),('cancel','Cancel'),], string='Status', related='uniform_demand_id.state', store=True, readonly=True, copy=False,)
	approved_qty = fields.Integer(string='Approved Qty')
	stock_lines = fields.One2many('stock.move', 'emp_id', string='Inventory Lines',compute='_compute_stock_lines')
	rfid = fields.Char("RFID")
	tracking = fields.Selection(related="item_id.product_id.tracking",string="Tracking")
	
	@api.model
	def create(self,vals):
		qty = vals.get('qty')	
		vals.update({
			'approved_qty': qty,
		})		
		return super(sos_uniform_demand_line, self).create(vals)

	@api.model
	def _get_uom_id(self):
		pdb.set_trace()
		try:
			proxy = self.env['ir.model.data']
			result = proxy.get_object_reference('product', 'product_uom_unit')
			return result[1]
		except Exception:
			return False
	
	@api.one	
	def unlink(self):
		if (self.uniform_demand_id and self.uniform_demand_id.state != 'draft') or (self.safety_demand_id and self.safety_demand_id.state != 'draft'):
			raise UserError(('You can delete the Entry whose demand is in the in Draft State.'))
		ret = super(sos_uniform_demand_line, self).unlink()
		return ret	

	@api.onchange('item_id')
	def onchange_item_id(self):
		context = self._context or {}
		res = {'value': {'req_size': False}}
		if not self.item_id:
			return res

		item = self.env['sos.uniform.items'].search([('id' ,'=', self.item_id.id)])			
		res['value'].update({'req_size': item.req_size})
		return res


class sos_uniform_dispatch_line(models.Model):		
	_name = "sos.uniform.dispatch.line"
	_description = "Uniform Dispatch Line"


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
	product_qty = fields.Integer(string='Qty')
	todo_qty = fields.Integer(string="To Do")
	lots_visible = fields.Boolean(string='Lots Visible')
	uniform_demand_id = fields.Many2one('sos.uniform.demand', string='Lines', index=True)
	rfid = fields.Char("RFID")
	button_pack_ids = fields.One2many('sos.pack.operation.lot', 'dispatch_line_id', string='Button Pack', index=True)

	
	@api.one
	@api.onchange('product_id')	
	def onchange_product_id(self):		
		#if not self.product_id:
		#	return True
		
		# - set a domain on product_uom
		#res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
		
		self.product_uom = self.product_id.uom_id
		
		#stock_qty = product_obj._product_available(cr, uid,[product.id], context={'location': 12})[product.id]['qty_available']
		#res['value'].update({'stock_qty': stock_qty})
		self.lots_visible = True if self.product_id.tracking == 'serial' else False
	
		qty = 0
		for item in self.uniform_demand_id.uniform_demand_line:
			#for prod in item.item_id.product_ids:
			for prod in item.item_id.product_id:
				if prod.id == self.product_id.id:
					qty += item.approved_qty
		self.todo_qty = qty			
					
	
	@api.multi
	def split_lot(self):
		context = self._context or {}
		ctx=context.copy()
		assert len(self.ids) > 0
		data_obj = self.env['ir.model.data']
		
		pack = self.browse(self.ids[0])
		view = data_obj.xmlid_to_res_id('sos_uniform.view_pack_operation_lot_form')

		ctx.update({'serial': True,
			})
		return {
			 'name': _('Lot Details'),
			 'type': 'ir.actions.act_window',
			 'view_type': 'form',
			 'view_mode': 'form',
			 'res_model': 'sos.uniform.dispatch.line',
			 'views': [(view, 'form')],
			 'view_id': view,
			 'target': 'new',
			 'res_id': pack.id,
			 'context': ctx,
		}
			
	
	@api.multi	
	def save(self):
		for pack in self:
			if pack.product_id.tracking != 'none':
				qty_done = sum([x.qty for x in pack.button_pack_ids])
				pack.write({'product_qty': qty_done})
		return {'type': 'ir.actions.act_window_close'}
	
	
	@api.onchange('rfid')
	def change_button(self):		
		button_obj = self.env['sos.button.inventory']
		pack_obj = self.env['sos.pack.operation.lot']
		if self.rfid:
			button_id = button_obj.search([('name','=',self.rfid),('state','=','main_store')])
			if button_id:		
				res = {
					'dispatch_line_id': self.env.context['active_id'],
					'rfid' : button_id.name,
				}
				rec_id = pack_obj.create(res)
				self.rfid = False
			
				pack_ids = pack_obj.search([('dispatch_line_id','=',self.env.context['active_id'])])
				self.button_pack_ids = pack_ids.ids	

