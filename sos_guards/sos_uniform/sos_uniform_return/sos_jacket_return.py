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


class sos_jacket_return(models.Model):		
	_name = "sos.jacket.return"
	_description = "Jacket Returns"
	_inherit = ['mail.thread']

	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True)
	project_id = fields.Many2one('sos.project', string = 'Project', index=True)
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True)
	return_number = fields.Integer(string='Return Number', required=True, readonly=True)
	employee_id = fields.Many2one('hr.employee', string = "Received By", domain=[('active','=',True)], required=True, index= True)           
	
	
	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'))
	state = fields.Selection([('draft','Draft'),('recommended','Recommended'),('reviewed','Reviewed'),('approved','Approved'),('dispatch','Dispatch'),('done','Done'),('rejected','Rejected'),('cancel','Cancelled'),], string='Status', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,)
	remarks = fields.Text(string='Remarks')
	
	jacket_return_line = fields.One2many('sos.jacket.return.line', 'jacket_return_id', string='Jacket Lines')
	
	product_ids = fields.Many2many('product.product','sos_product_jacket_return', 'product_id', 'demand_id', string='Products')
	guard_id = fields.Many2one('hr.guard', string='Guards',readonly=True)
	guard_employee_id = fields.Many2one('hr.employee', string='Employee',readonly=True)
	
	_defaults = {
		'return_number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').next_by_code(cr, uid, 'sos.jacket.return'),
	}

	@api.multi
	@api.depends('name', 'return_number')
	def name_get(self):
		res = []
		for record in self:
			name = record.return_number
			name = "Return -" + ' ' +str(name)
			res.append((record.id, name))
		return res
	
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.jacket.return')
		vals.update({
			'return_number': st_number,
		})
		return super(sos_jacket_return, self).create(vals)
	
	
	@api.multi	
	def demand_recommended(self):
		for demand in self:		
			demand.write({'state':'recommended'})
		return True
	
	@api.multi
	def demand_reviewed(self):
		for demand in self:	
			demand.write({'state':'reviewed'})
		return True	

	@api.multi
	def demand_approved(self):
		for demand in self:	
			demand.write({'state':'approved'})
		return True

	@api.multi
	def demand_dispatch(self):
		for demand in self:	
			demand.write({'state':'done'})
		return True
	
	@api.multi
	def demand_rejected(self):
		for demand in self:		
			demand.write({'state':'rejected'})
		return True
	

class sos_jacket_return_line(models.Model):		
	_name = "sos.jacket.return.line"
	_description = "Jacket Return Line"
	
	item = fields.Selection([('jersey','Jersey'),('jacket','Jacket'),('raincoat','Rain Coat'),], string='Item', index=True, default='jersey', copy=False,)
	qty = fields.Integer(string='Qty')
	size = fields.Char(string='Size')
	jacket_return_id = fields.Many2one('sos.jacket.return', string='Lines', index=True)
