import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class sos_jacket_demand(models.Model):		
	_name = "sos.jacket.demand"
	_description = "Jackets Demand"
	_inherit = ['mail.thread']
	_order = "date desc"

	@api.one
	@api.depends('new_guards', 'existing_guards')
	def _compute_total(self):
		self.no_of_guards = self.new_guards + self.existing_guards
	
	@api.one
	@api.depends('move_id','state')
	def _compute_dispatch_lines(self):
		lines = self.env['stock.move'].search([('jacket_demand_id', '=', self.id)])
		self.dispatch_ids = lines.sorted()	

	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True)
	project_id = fields.Many2one('sos.project', string = 'Project', index=True)
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True)
	employee_id = fields.Many2one('hr.employee', string = "Requested By", domain=[('is_guard','=',False),('active','=',True)], index= True)
	name = fields.Char(string='Demand Number', readonly=True,size=16)
	
	new_posts = fields.Boolean(string='New Post', track_visibility='onchange')
	new_guards = fields.Integer(string='New Guards', track_visibility='onchange')
	existing_guards = fields.Integer(string='Existing Guards', track_visibility='onchange')
	no_of_guards = fields.Integer(string='Total Guards', compute='_compute_total',readonly=True)
	
	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'))
	state = fields.Selection([('draft','Draft'),('recommended','RM'),('reviewed','Coordinator'),('approved','HOC'),('adm','Admin'),('dispatch','Store'),('done','Delivered'),('rejected','Rejected'),('cancel','Cancelled'),], string='Status', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,)
	remarks = fields.Text(string='Remarks')
	delivery_date = fields.Date(string='Delivery Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'dispatch': [('readonly', False)]})
	product_ids = fields.Many2many('product.product','sos_product_jacket_demand', 'product_id', 'demand_id', string='Products')
	guard_ids = fields.Many2many('hr.employee','guard_jacket_demand', 'guard_id', 'demand_id', string='Guards')
	
	jacket_demand_line = fields.One2many('sos.jacket.demand.line', 'jacket_demand_id', string='Jacket Lines')
	jacket_dispatch_line = fields.One2many('sos.jacket.dispatch.line', 'jacket_demand_id', string='Dispatch Lines', readonly=True, states={'review': [('readonly', False)],'approve': [('readonly', False)]})
	move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True,)
	dispatch_ids = fields.Many2many('stock.move', string='Dispatch Moves', compute='_compute_dispatch_lines')
	dispatch_date = fields.Date('Dispatch Date',readonly=True,)
	dm_type = fields.Selection([('new_deployment','New Deployment'),('complain','Complain'),('additional_guard','Additional Guard'),('replacement','Replacement')], string='Type')

	@api.multi
	@api.depends('name')
	def name_get(self):
		res = []
		for record in self:
			name = record.name
			name = "Demand -" + ' ' + name
			res.append((record.id,name))
		return res
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.jacket.demand')
		vals.update({
			'name': st_number,
		})		
		return super(sos_jacket_demand, self).create(vals)
	
	@api.multi	
	def demand_recommended(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'recommended'})
		return True
	
	@api.multi
	def demand_reviewed(self):
		context = self._context or {}
		for demand in self:	
			demand.write({'state':'reviewed'})
		return True	
	
	@api.multi
	def demand_approved(self):
		context = self._context or {}
		for demand in self:			
			demand.write({'state':'approved'})
		return True
		
	@api.multi
	def demand_admin(self):
		for demand in self:
			demand.sudo().write({'state':'adm'})	

	@api.multi
	def demand_dispatch(self):
		context = self._context or {}
		stock_move = self.env['stock.move']
		
		for demand in self:
			dispatch_date =	datetime.today().strftime('%Y-%m-%d')
			if not demand.jacket_dispatch_line:
				raise Warning(_('Please Enter the Dispatch Items.'))
				
			# Make the Dictionary of required items with Qty		
			req_prods = {}
			for item in demand.jacket_demand_line:
				for prod in item.item.product_id:
					qty = req_prods.get(prod.id,0) 
					req_prods.update({prod.id: qty+item.approved_qty})
			
			#If matching the Dispatched and required quantities	
			for item in demand.jacket_dispatch_line:
				qty = req_prods.get(item.product_id.id,0) 
				qty = qty-item.product_qty
				if qty == 0:
					req_prods.pop(item.product_id.id, None)
				else:					
					req_prods.update({item.product_id.id: qty})
			
			# removed on the request of zahid		
			#if req_prods:
			#	raise Warning(_('Approved & Dispatched Items does not match.'))
			
			for item in demand.jacket_dispatch_line:
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
					'jacket_demand_id': demand.id,
				}				
				stock_move_id = stock_move.create(vals) 
				stock_move_id._action_done()
		self.write({'state':'dispatch','dispatch_date':dispatch_date})
	
	@api.multi	
	def demand_delivered(self):
		context = self._context or {}
		
		stock_move = self.env['stock.move']
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']
		
		for demand in self:
			for line in demand.jacket_demand_line:
				if not line.guard_id:
					raise Warning(_('Please Enter the Guard Names.'))
		delivery_date = demand.delivery_date
	
		amount = 0
		for item in demand.jacket_demand_line:
			for product in item.item.product_id:
				vals = {
					'date': delivery_date,
					'origin': demand.name,
					'product_uom_qty': item.qty,
					'product_uom': product.uom_id.id,

					'location_id': demand.center_id.stock_location_id.id,
					#'location_dest_id': 25,
					'location_dest_id': 9,

					'partner_id': 1,
					'state': 'draft',
					'warehouse_id': 1,

					'name': demand.name + ":" + product.name,
					'product_id': product.id,	
					'emp_id': item.guard_id.id,
					'uniform_demand_id': demand.id,
				}
				stock_move_id = stock_move.create(vals) 
				stock_move_id._action_done()
				amount += item.qty * product.list_price

		move_lines=[]
		move_lines.append((0,0,{
			'name': demand.name,
			'debit': amount,
			'credit': 0.0,
			'account_id': 139,	 # Uniform Exp 41010				
			'journal_id': 9,  # Stock Journal			
			'date': delivery_date,
			'jacket_demand_id': demand.id,
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
			'jacket_demand_id': demand.id,
			'post_id': demand.post_id.id,
		}))
		move = {
			'ref': demand.name,
			'name': demand.name,
			'journal_id': 9,  # Stock Journal
			'date': delivery_date,
			'post_id': demand.post_id.id,
			'narration': demand.name + ":Regular:" + str(demand.date),
			'line_ids': move_lines,					
		}

		move_id = move_obj.sudo().create(move)
		move_id.state = 'posted'		
		demand.write({'state':'done','move_id':move_id.id})
	
	@api.multi
	def demand_rejected(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'rejected'})
		return True

	@api.multi
	def demand_required_item_dispatch(self):
		for demand in self:
			if not demand.jacket_dispatch_line:
				for line in demand.jacket_demand_line:
					vals = {
						'product_id' : line.item.product_id.id,
						#'stock_qty' : 0,
						'product_qty' : line.qty,
						'jacket_demand_id' : demand.id,
						'product_uom' : 1,
						}
					dispatch_line = self.env['sos.jacket.dispatch.line'].create(vals)	
			else:
				raise Warning(_('Dispatched Items Already Entered.'))


class sos_jacket_demand_line(models.Model):		
	_name = "sos.jacket.demand.line"
	_description = "Jackets Demand Line"
	
	@api.one
	def _compute_stock_lines(self):
		related_recordset = self.env["stock.move"].search([('emp_id','=',self.guard_id.id)])
		self.stock_lines = related_recordset.ids

	#item = fields.Selection([('jersey','Jersey'),('jacket','Jacket'),('raincoat','Rain Coat'),], string='Item', index=True, default='jersey', copy=False,)
	item = fields.Many2one('sos.uniform.items',string='Item')
	qty = fields.Integer(string='Qty')
	size = fields.Char(string='Size')
	guard_id = fields.Many2one('hr.employee',string='Guard',required=True)
	date = fields.Date(string='Last Inssuance' ,required=False)
	state = fields.Selection([('draft','Draft'),('recommended','RM'),('reviewed','Coordinator'),('approved','HOC'),('adm','Admin'),('dispatch','Store'),('done','Delivered'),('rejected','Rejected'),('cancel','Cancelled')], string='Status', related='jacket_demand_id.state', store=True, readonly=False, copy=False)
	approved_qty = fields.Integer(string='Approved Qty')
	stock_lines = fields.One2many('stock.move', 'emp_id', string='Inventory Lines',compute='_compute_stock_lines')
	jacket_demand_id = fields.Many2one('sos.jacket.demand', string='Lines', index=True)
	
	
class sos_jacket_dispatch_line(models.Model):		
	_name = "sos.jacket.dispatch.line"
	_description = "Jacket Dispatch Line"

	# def _get_uom_id(self):
	# 	try:
	# 		proxy = self.env['ir.model.data']
	# 		result = proxy.get_object_reference('product', 'product_uom_unit')
	# 		return result[1]
	# 	except Exception, ex:
	# 		return False

	product_id = fields.Many2one('product.product',string='Product')
	product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)
	stock_qty = fields.Float(string='Stock Qty')
	product_qty = fields.Integer(string='Qty')
	jacket_demand_id = fields.Many2one('sos.jacket.demand', string='Lines', index=True)