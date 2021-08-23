import pdb
from datetime import datetime
from odoo import tools
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class SOSPost(models.Model):
	_description = "SOS Posts"
	_name = 'sos.post'
	_inherit = ['mail.thread']
	_inherits = {
		'res.partner': "partner_id",		
	}
	_order = 'name'

	
	@api.one	
	@api.depends('employee_ids','employee_ids.current','job_ids','job_ids.guards')
	def _get_current_fnc(self):
		overstaffing = False
		guard_count = self.env['sos.guard.post'].search_count([('post_id', '=', self.id),('current', '=', True)])
		self.cur_guards = guard_count
		if guard_count > self.guards:
			overstaffing = True
		self.is_overstaffed = overstaffing							
	
	postcity_id = fields.Many2one('sos.city', 'Post City')
	partycode = fields.Char('Party Code', size=16)
	startdate = fields.Date('Start Date',track_visibility='onchange')
	enddate = fields.Date('End Date',track_visibility='onchange')

	guardrate = fields.Integer('Unarmed Guard Rate',track_visibility='onchange')
	guardarmedrate = fields.Integer('Armed Guard Rate',track_visibility='onchange')
	seniorguardrate = fields.Integer('Senior Guard Rate',track_visibility='onchange')
	supervisorrate = fields.Integer('Supervisor Rate',track_visibility='onchange')	
	mujahidrate = fields.Integer('Mujahid Guard Rate',track_visibility='onchange')
	searcherdrate = fields.Integer('Lady Searcher Rate',track_visibility='onchange')

	paidon = fields.Boolean('Paidon')
	center_id = fields.Many2one('sos.center', string = 'Center')
	region_id = fields.Many2one('sos.region', string = 'Region',related='center_id.region_id',store=True)


	guards = fields.Integer('Guards', help='Maximum guards at the post',track_visibility='onchange')
	insurance = fields.Char('Insurance', size=32,track_visibility='onchange')
	gst = fields.Char(string='GST', size=32,track_visibility='onchange')
	taxrate_id = fields.Many2one('account.tax', string = 'Tax Rate',domain=[('account_id','!=',False)],track_visibility='onchange')

	ntn = fields.Char('NTN', size=32)
	stno = fields.Char('Sales Tax No.', size=32)
	bank = fields.Char('Bank Name', size=64)
	bankacc = fields.Char('Bank Account', size=32, track_visibility='onchange')
	headoffice = fields.Many2one('sos.partneraddress', string = 'Head Office')

	project_id = fields.Many2one('sos.project', string = 'Project', help = 'Project related to this Post')
	address_id = fields.One2many('sos.partneraddress', 'post_id' , string = 'Address', help = 'Address')
	
	cur_guards = fields.Integer(compute='_get_current_fnc', string='Current Guards', store = True, track_visibility='onchange')
	is_overstaffed = fields.Boolean(compute='_get_current_fnc', string='Over Staffed', store = True)
	
	partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='cascade', auto_join=True, track_visibility='onchange')	
	ftn = fields.Char('NTN/FTN', size=32)
	strn =  fields.Char('STRN', size=32)
	
	to_be_processed = fields.Boolean(default=True, track_visibility='onchange')
	central = fields.Boolean('Central Post', track_visibility='onchange')
	attendance_min_date = fields.Date('Min. Attendance Date',write=['sos.group_superusers'])
	attendance_max_date = fields.Date('Max. Attendance Date',write=['sos.group_superusers'])
	
	morning_shift_guards = fields.Integer('Morning Shift Guards', help='Morning Shift guards at the post',track_visibility='onchange')
	evening_shift_guards = fields.Integer('Evening Shift Guards', help='Evening Shift guards at the post',track_visibility='onchange')
	
	employee_ids = fields.One2many('sos.guard.post', 'post_id', 'Guards History')
	remark_ids = fields.One2many('sos.post.remarks', 'post_id', 'Notes about Post')
	job_ids = fields.One2many('sos.post.jobs', 'post_id', 'Jobs at Post', track_visibility='onchange')
	weapon_lines = fields.One2many('sos.weapon.post', 'post_id', string='Weapons')
	
	@api.model
	def set_receivable_payable_cron(self):
		recs = False
		recs = self.env['sos.post'].search(['|',('property_account_receivable_id', '=', False),('property_account_payable_id','=',False)])
		if recs:
			for rec in recs:
				_logger.info('.......Post set True ... %r ..............', rec.post_id.name)
				rec.to_be_processed = True
	
	@api.model
	def process_receivable_payable_cron(self):
		recs = False
		recs = self.env['sos.post'].search([('to_be_processed','=',True)], limit=100)
		if recs:
			for rec in recs:
				_logger.info('.......Process the Post  ... %r ..............', rec.post_id.name)
				rec.partner_id.property_account_receivable_id = 48
				rec.partner_id.property_account_payable_id = 344
				rec.to_be_processed = False


class sos_post_jobs(models.Model):
	_description = "SOS Post Jobs"
	_name = 'sos.post.jobs'
	
	post_id = fields.Many2one('sos.post', string = 'Post', help = 'Post related to this Record')
	contract_id = fields.Many2one('guards.contract', 'Contract')
	product_id = fields.Many2one('product.product', 'Product', domain=[('product_tmpl_id.sale_ok','=',True)], ondelete='set null')
	guards = fields.Integer('Guards')
	rate = fields.Integer('Guard Rate')


class SOSPostRemarks(models.Model):
	_name = 'sos.post.remarks'
	_description = "SOS POST Remarks"
	_order = 'note_date desc'
	
	post_id = fields.Many2one('sos.post', string = 'Post')
	user_id = fields.Many2one('res.users', string = 'User',default=lambda self: self.env.user)
	notes = fields.Text('Notes')
	note_date = fields.Date('Date',default=fields.Date.today())
	
	
class SOSGuardPost(models.Model):
	_name = "sos.guard.post"
	_description = "SOS Guard Posts"
	_order = 'fromdate desc'
	
	employee_id = fields.Many2one('hr.employee', string = 'Employee',required=True)				
	guard_id = fields.Many2one('hr.guard', string = 'Guard',required=True)
	center_id = fields.Many2one('sos.center',related='employee_id.center_id',string='Center',store=True)	
	project_id = fields.Many2one('sos.project', string = 'Project', help = 'Project...')
	post_id = fields.Many2one('sos.post',required=True, string = 'Post', help = 'Post...')
	fromdate = fields.Date('From Date',required=True)
	todate = fields.Date('To Date')
	current = fields.Boolean('Current Post',default=1)
	remarks = fields.Char('Remarks', size=64)
	to_reason = fields.Selection([('transfer','Transfer'),('terminate','Terminate'),('escape','Escaped')],'Reason',help='Select the Reason of To-Date')
	processed = fields.Boolean(default=False)
		

