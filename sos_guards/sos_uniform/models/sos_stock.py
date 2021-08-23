import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

		
class stock_move(models.Model):
	_name = "stock.move"
	_inherit = "stock.move"
    
	post_id = fields.Many2one('sos.post', string = 'Post')
	emp_id = fields.Many2one('hr.employee', string = 'Employee')
	center_id = fields.Many2one('sos.center', string = 'Center')
	uniform_demand_id = fields.Many2one('sos.uniform.demand', string = 'Uniform Demand')
	weapon_demand_id = fields.Many2one('sos.weapon.demand', string = 'Weapon Demand')
	stat_demand_id = fields.Many2one('sos.stationery.demand', string = 'Stationery Demand')
	rf_id = fields.Char('RF ID')
	jacket_demand_id = fields.Many2one('sos.jacket.demand', string = 'Jacket Demand')
	
class stock_location(models.Model):
	_name = "stock.location"
	_inherit = "stock.location"
    
	user_ids = fields.Many2many('res.users', 'stock_location_user_rel', 'location_id', 'user_id', 'Users')
	

class sos_center(models.Model):
	_name = "sos.center"
	_inherit = "sos.center"
    
	stock_location_id = fields.Many2one('stock.location','Stock Location')
	
class hr_employee(models.Model):
	_name = 'hr.employee'
	_inherit = 'hr.employee'
	
	stock_lines = fields.One2many('stock.move', 'emp_id', string='Inventory Lines')
	
class sos_post(models.Model):
	_name = 'sos.post'
	_inherit = 'sos.post'
	
	stock_lines = fields.One2many('stock.move', 'post_id', string='Inventory Lines')
	
class sos_center(models.Model):
	_name = 'sos.center'
	_inherit = 'sos.center'
	
	stat_stock_lines = fields.One2many('stock.move', 'center_id', string='Stationery Lines')	
	
	
	
class res_partner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	@api.multi
	def _journal_item_count(self):
		for partner in self:
			partner.journal_item_count = self.env['account.move.line'].search_count([('partner_id', '=', partner.id),('account_id.internal_type', 'in', ['receivable', 'payable'])])
			partner.contracts_count = self.env['account.analytic.account'].search_count([('partner_id', '=', partner.id)])
	
	
	@api.one
	def _compute_dispatch(self):
		self.reconcible_item_count = self.env['account.move.line'].search_count([('partner_id', '=', self.id),('account_id.reconcile', '=', False),('account_id.type', 'in', ['receivable', 'payable'])])
		
	reconcible_item_count =  fields.Integer("Reconcible Item", compute='_compute_dispatch')
	

# this model is not found in odoo 12 :Remark by Numan: 
	
#class stock_pack_operation(models.Model):
#	_name = "stock.pack.operation"
#	_inherit = "stock.pack.operation"
	
	
#	@api.onchange('rf_id')
#	def change_button(self):		
#		button_obj = self.env['sos.button.inventory']
#		lot_obj = self.env['stock.pack.operation.lot']
#		if self.rf_id:
#			button_id = button_obj.search([('name','=',self.rf_id),('state','=','stitching')])
#			if button_id:
#								
#				res = {
#					'operation_id': self.env.context['active_id'],
#					'lot_name' : button_id.name,
#				}
#				rec_id = lot_obj.create(res)
#				self.rf_id = False
#			
#				lot_ids = lot_obj.search([('operation_id','=',self.env.context['active_id'])])
#				self.pack_lot_ids = lot_ids.ids
#	# Column #		
#	rf_id = fields.Char('Button')
	
	
class stock_picking(models.Model):
	_name = "stock.picking"
	_inherit = "stock.picking"
	
	
	@api.multi
	def do_transfer(self):
		result = super(stock_picking, self).do_transfer()
		for rec in self:
			pro_ids = rec.pack_operation_product_ids
			for pro_id in pro_ids:
				lot_ids = pro_id.pack_lot_ids
				for lot_id in lot_ids:
					rf_id = self.env['sos.button.inventory'].search([('name','=',lot_id.lot_name)])
					if rf_id:
						rf_id.state="main_store"
		return result
		
class sos_pack_operation_lot(models.Model):
	_name = "sos.pack.operation.lot"
	_description = 'SOS Pack Operation Lot'
    
    
	dispatch_line_id = fields.Many2one('sos.uniform.dispatch.line')
	qty = fields.Integer('Done',default=1)
	rfid = fields.Char('RFID')
	
	
