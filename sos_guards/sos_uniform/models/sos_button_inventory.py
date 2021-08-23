import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


###  Button Inventory ###
		
class sos_button_inventory(models.Model):
	_name = "sos.button.inventory"
	
	_inherit = ['mail.thread']
	_order = "name, state"
	
	_track = {
	}
    
	name = fields.Char('Name')
	entry_date = fields.Date(string='Entry Date' ,required=False, default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	state = fields.Selection([('draft','Not Used (Head Office Store)'),('branch_store','Not Used (Regional Office Store)'),('guard','Guard')],'Status',default='draft',track_visibility='onchange')
	remarks = fields.Text('Description',track_visibility='onchange')
	
	
	_sql_constraints = [
		('name_uniq', 'unique(name)', 'Duplicate entry of Button is not allowed!')
		]
	
	@api.model
	def create(self, vals):		
		found = self.search([('name','=',vals['name'])])
		if found:
			raise UserError(('Record Already Exist'))
			return
		else:
			result = super(sos_button_inventory, self).create(vals)
			return result
		
			
	@api.one	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete the Record which are not in Draft State. Please Shift First in Draft state then delete it.'))
		ret = super(sos_button_inventory, self).unlink()
		return ret
		

### Inventory Issuance ###
	
class sos_button_tailor_issuance(models.Model):
	_name = "sos.button.tailor.issuance"
	
	_inherit = ['mail.thread']
	_order = "id desc"
	
	_track = {
	}
	
	
	@api.onchange('dummy')
	def change_dummy(self):		
		button_obj = self.env['sos.button.inventory']
		if self.dummy:
			button_id = button_obj.search([('name','=',self.dummy)])
			if button_id:				
				self.button_ids = [(6,0,(self.button_ids + button_id).ids)]
			self.dummy = False	
	
	name = fields.Char('Name', required=True)
	date = fields.Date(string='Date' ,required=False, default=lambda self: datetime.today().strftime('%Y-%m-%d'), track_visibility='onchange')	
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Done'),('cancel','Cancel')],'Status',default='draft', track_visibility='onchange')
	button_ids = fields.Many2many('sos.button.inventory',string='Buttons', track_visibility='onchange')
	
	employee_id = fields.Many2one('hr.employee', string = "Guard", index= True)
	center_id = fields.Many2one('sos.center', related="employee_id.center_id", string='Center',required=False, index=True , store=True, track_visibility='onchange')
	project_id = fields.Many2one('sos.project', related="employee_id.project_id", required=False, string = 'Project', index=True, store=True,  track_visibility='onchange')
	post_id = fields.Many2one('sos.post',related="employee_id.current_post_id" ,string = 'Post', index=True, required=False, store=True, track_visibility='onchange')
	
	dummy = fields.Char('Button No.')
	remarks = fields.Text('Description',track_visibility='onchange')
	
		
	@api.one	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete the Record which are not in Draft State. Please Shift First in Draft state then delete it.'))
		ret = super(sos_button_tailor_issuance, self).unlink()
		return ret	

	
	@api.multi
	def inventory_confirm(self):
		for rec in self:
			for r in rec.button_ids:
				r.state = "branch_store"
		self.write({'state':'confirm'})
		
	@api.multi
	def inventory_done(self):
		rf_id = self.env['employee.rfid']
		for rec in self:
			for r in rec.button_ids:
				r.state = "guard"
				vals = {
					'employee_id' : rec.employee_id.id,
					'rf_id' : r.name,
					'state' : 'done',
					}
				rf_id.create(vals)	
		self.write({'state':'done'})
		
	@api.multi
	def inventory_cancel(self):
		self.write({'state':'cancel'})			
	
	
