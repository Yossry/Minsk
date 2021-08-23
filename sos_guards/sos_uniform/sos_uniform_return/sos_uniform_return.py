import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import itertools
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class SOSUniformReturn(models.Model):
	_name = "sos.uniform.return"
	_description = "Uniform Returns"
	_inherit = ['mail.thread']

	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True)
	project_id = fields.Many2one('sos.project', string = 'Project', index=True,required=True)
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True)
	name = fields.Char(string='Return Number', readonly=True)
	employee_id = fields.Many2one('hr.employee', string = "Received By", domain=[('active','=',True)], required=True, index= True)

	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'))
	state = fields.Selection([('draft','Draft'),('open','Open'),('review','Review'),('approve','Approve'),('receive','Receive'),('done','Done'),('reject','Reject'),('cancel','Cancel'),], string='Status', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,)
	remarks = fields.Text(string='Remarks')
	receive_date = fields.Date('Receive Date')
	uniform_return_line = fields.One2many('sos.uniform.return.line', 'uniform_return_id', string='Uniform Return Lines')
	product_ids = fields.Many2many('product.product','sos_product_uniform_return', 'product_id', 'return_id', string='Products')
	guard_id = fields.Many2one('hr.guard', string='Guards',required=True)
	guard_employee_id = fields.Many2one('hr.employee', string='Employee',readonly=True)
	dm_type = fields.Selection([('new_deployment','New Deployment'),('complain','Complain'),('additional_guard','Additional Guard'),('replacement','Replacement')], string='Type')	
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.uniform.return')
		vals.update({
			'name': st_number,
		})
		return super(SOSUniformReturn, self).create(vals)

	@api.multi
	def write(self,vals):
		obj_seq = self.env['ir.sequence']
		context = self._context or {}
		
		for rec in self:
			if not rec.name:
				st_number = obj_seq.next_by_code('sos.uniform.return')
				vals.update({
					'name': st_number,
				})	
		return super(SOSUniformReturn, self).write(vals)

	@api.multi	
	def demand_open(self):
		for demand in self:		
			demand.write({'state':'open'})
		return True
	
	@api.multi
	def demand_review(self):
		for demand in self:			
			demand.write({'state':'review'})
		return True	

	@api.multi
	def demand_approve(self):
		for demand in self:		
			demand.write({'state':'approve'})
		return True

	@api.multi
	def demand_receive(self):
		stock_move = self.env['stock.move']		
		context = self._context or {}

		for demand in self:
			receive_date = demand.date			#demand.date < '2014-04-10' and demand.date or time.strftime('%Y-%m-%d')
			period_ids = self.env['sos.period'].find(receive_date)
			period_id = period_ids and period_ids[0] or False

			#if not demand.uniform_return_line:
			#	raise Warning(_('Please Enter the Received Items.'))

			for item in demand.product_ids:
				vals = {
					'date': receive_date,
					'origin': demand.name,
					'product_uom_qty': 1.0,
					'product_uom': 1,
					#'price_unit': item.id.list_price,

					'location_id': 25,
					'location_dest_id': demand.center_id.stock_location_id.id,

					'partner_id': 1,
					'state': 'draft',
					'warehouse_id': 1,

					'name': demand.name + ": " + item.name_template,
					'product_id': item.id,
					#'uniform_return_id': demand.id,
				}				
				stock_move_id = stock_move.create(vals,) 
				stock_move_id.action_done()

			demand.write({'state':'receive','receive_date':receive_date})
		return True
	
	@api.multi
	def demand_reject(self):
		for demand in self:	
			demand.write({'state':'reject'})
		return True
	

class SOSUniformReturnLine(models.Model):
	_name = "sos.uniform.return.line"
	_description = "Uniform Return Line"

	item_id = fields.Many2one('sos.uniform.return.items',string='Return Items')
	qty = fields.Integer(string='Qty',default=1,)
	req_size = fields.Boolean(string='Size Required?')
	size = fields.Char(string='Size')
	uniform_return_id = fields.Many2one('sos.uniform.return', string='Lines', index=True)
	date = fields.Date(string='Receive Date' ,required=False)
	
	@api.onchange('item_id')
	def onchange_item_id(self):
		context = self._context or {}
		res = {'value': {'req_size': False}}
		if not self.item_id:
			return res

		item = self.env['sos.uniform.return.items'].search([('id', '=', self.item_id.id)])			
		res['value'].update({'req_size': item.req_size})
		return res


class SOSUniformReturnItems(models.Model):
	_name = "sos.uniform.return.items"
	_description = "Uniform Return Items"
	
	name = fields.Char('Item Name')
	req_size = fields.Boolean(string='Size Required?')
	product_ids = fields.Many2many('product.product','sos_uniform_return_product', 'return_item_id', 'return_product_id', string='Items')