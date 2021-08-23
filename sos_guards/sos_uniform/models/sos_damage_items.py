import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class sos_damage_demand(models.Model):		
	_name = "sos.damage.demand"
	_description = "Damage Demand"
	_inherit = ['mail.thread']
	_order = "date desc"
	_track = {
	}
	
	name = fields.Char(string='Demand Number',readonly=True, track_visibility='onchange')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True,track_visibility='onchange')
	project_id = fields.Many2one('sos.project', string = 'Project', index=True,track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee', string = "Requested By", domain=[('is_guard','=',False),('active','=',True)],index= True)
	
	date = fields.Date(string='Demand Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'))
	state = fields.Selection([('draft','Draft'),('approve','Approved'),('done','Discard'),('rejected','Rejected'),('cancel','Cancelled'),], string='Status', index=True, default='draft',track_visibility='onchange', copy=False,)
	
	damage_line = fields.One2many('sos.damage.demand.line', 'damage_id', string='Received Lines')
	remarks = fields.Text(string='Remarks')
		
	@api.multi
	@api.depends('name')
	def name_get(self):
		res = []
		for record in self:
			name = record.name
			name = "Demage -" + ' ' + name
			res.append((record.id,name))
		return res
	
	@api.model
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.damage.demand')
		vals.update({
			'name': st_number,
		})		
		return super(sos_damage_demand, self).create(vals)
		
	@api.multi
	def demand_approved(self):
		context = self._context or {}
		for demand in self:			
			demand.write({'state':'approve'})
		return True
	
	@api.multi
	def demand_discard(self):
		context = self._context or {}
		for demand in self:			
			demand.write({'state':'done'})
		return True
	
	@api.multi
	def demand_rejected(self):
		context = self._context or {}
		for demand in self:		
			demand.write({'state':'rejected'})
		return True				


class sos_damage_demand_line(models.Model):		
	_name = "sos.damage.demand.line"
	_description = "Damage Demand Line"
	
	name = fields.Char(string='Name')
	item = fields.Selection([('uniform','Uniform'),('shoes','Shoes'),('cap','Cap'),('belt','Belt'),('shirt','T-Shirt'),('jersy','Jersy'),('trouser','Trouser'),('jacket','Jacket'),('rain_coat','Rain Coat'),('metal_detector','Metal Detector'),], string='Items Received', index=True, copy=False,)
	qty = fields.Integer(string='Qty')
	size = fields.Char(string='Size')
	damage_id = fields.Many2one('sos.damage.demand', string='Lines', index=True)
	
	
