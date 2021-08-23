import calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import common_timezones, timezone, utc
from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import tools
import math
import pdb

STATE_COLOR_SELECTION = [
	('0', 'Red'),
	('1', 'Green'),
	('2', 'Blue'),
	('3', 'Yellow'),
	('4', 'Magenta'),
	('5', 'Cyan'),
	('6', 'Black'),
	('7', 'White'),
	('8', 'Orange'),
	('9', 'SkyBlue')
	]

class AccountAssetCategory(models.Model):
	_inherit = 'account.asset.category'
	
	#cols	
	abbrev = fields.Char("Abbrev",size=2)

class stock_location(models.Model):
	_inherit = "stock.location"

	#cols
	code = fields.Char("Code",size=2)


class asset_state(models.Model):
	_name = 'asset.state'
	_description = 'State of Asset'
	_order = "sequence"

	STATE_SCOPE_TEAM = [
		('0', 'Finance'),
		('1', 'Warehouse'),
		('2', 'Manufacture'),
		('3', 'Maintenance'),
		('4', 'Accounting')
	]

	name = fields.Char('State', size=64, required=True, translate=True)
	sequence = fields.Integer('Sequence', default=1,help="Used to order states.")
	state_color = fields.Selection(STATE_COLOR_SELECTION, 'State Color')
	team = fields.Selection(STATE_SCOPE_TEAM, 'Scope Team')

	@api.multi
	def change_color(self):
		for state in self:
			color = int(state.state_color) + 1
			if (color>9): color = 0
			return state.write({'state_color': str(color)})


class asset_category(models.Model):
	_description = 'Asset Tags'
	_name = 'asset.category'

	name = fields.Char('Tag', required=True, translate=True)
	asset_ids = fields.Many2many('asset.asset', id1='category_id', id2='asset_id', string='Assets')

class asset_asset(models.Model):
	_name = 'asset.asset'
	_description = 'Asset'
	_inherit = ['mail.thread']

	@api.model
	def recompute_totals(self,nlimit=100):		
		assets = self.search([('to_be_processed','=',True)],limit=nlimit)
		for asset in assets:		
			asset._get_asset_code()
			asset.to_be_processed = False

	def _get_image(self,name, args, context=None):
		result = dict.fromkeys(self.ids, False)
		for obj in self:
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self,name, value, args, context=None):
		return self.write({'image': tools.image_resize_image_big(value)}, context=context)
		
	def _read_group_state_ids(self, domain, read_group_order=None, access_rights_uid=None, context=None, team='3'):
		access_rights_uid = access_rights_uid or uid
		stage_obj = self.env['asset.state']
		order = stage_obj._order
		
		# lame hack to allow reverting search, should just work in the trivial case
		if read_group_order == 'stage_id desc':
			order = "%s desc" % order
		
		search_domain = []
		search_domain += ['|', ('team','=',team)]
		search_domain += [('id', 'in', ids)]
		stage_ids = stage_obj._search(search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
		result = stage_obj.name_get(access_rights_uid, stage_ids, context=context)
		# restore order of the search
		result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))
		return result, {}

	def _read_group_finance_state_ids(self,read_group_order=None, access_rights_uid=None, context=None):
		return self._read_group_state_ids(domain, read_group_order, access_rights_uid, context, '0')

	def _read_group_warehouse_state_ids(self,domain, read_group_order=None, access_rights_uid=None, context=None):
		return self._read_group_state_ids(domain, read_group_order, access_rights_uid, context, '1')

	def _read_group_manufacture_state_ids(self, domain, read_group_order=None, access_rights_uid=None, context=None):
		return self._read_group_state_ids(domain, read_group_order, access_rights_uid, context, '2')

	def _read_group_maintenance_state_ids(self,domain, read_group_order=None, access_rights_uid=None, context=None):
		return self._read_group_state_ids(domain, read_group_order, access_rights_uid, context, '3')

	CRITICALITY_SELECTION = [
		('0', 'General'),
		('1', 'Important'),
		('2', 'Very important'),
		('3', 'Critical')
	]
	
	name = fields.Char('Asset Name', size=64, required=True, translate=True,track_visibility='onchange')
	finance_state_id = fields.Many2one('asset.state', 'State', domain=[('team','=','0')],track_visibility='onchange')
	warehouse_state_id = fields.Many2one('asset.state', 'State', domain=[('team','=','1')],track_visibility='onchange')
	manufacture_state_id = fields.Many2one('asset.state', 'State', domain=[('team','=','2')],track_visibility='onchange')
	maintenance_state_id = fields.Many2one('asset.state', 'State', domain=[('team','=','3')],track_visibility='onchange')
	maintenance_state_color = fields.Selection(STATE_COLOR_SELECTION, related='maintenance_state_id.state_color',string="Color", readonly=True,track_visibility='onchange')
	criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality')
	
	location_id = fields.Many2one('stock.location', string="Asset Location",track_visibility='onchange',help="This location will be used as the destination location for installed parts during asset life.")
	user_id = fields.Many2one('res.users', 'Assigned to', track_visibility='onchange')
	active = fields.Boolean('Active',track_visibility='onchange',default=True)
	
	model = fields.Char('Model', size=64,track_visibility='onchange')
	serial = fields.Char('Serial no.', size=64,track_visibility='onchange')
	vendor_id = fields.Many2one('res.partner', 'Vendor',track_visibility='onchange')
	manufacturer_id = fields.Many2one('res.partner', 'Manufacturer',track_visibility='onchange')
	start_date = fields.Date('Start Date',track_visibility='onchange')
	purchase_date = fields.Date('Purchase Date',track_visibility='onchange')
	warranty_start_date = fields.Date('Warranty Start',track_visibility='onchange')
	warranty_end_date = fields.Date('Warranty End',track_visibility='onchange')
	
	category_ids = fields.Many2many('asset.category', id1='asset_id', id2='category_id', string='Tags')
	category_id = fields.Many2one('account.asset.category','Category',required=True)
	department_id = fields.Many2one('hr.department','Department',required=False)
	company_id = fields.Many2one('res.company','Company',required=True)
	
	asset_number = fields.Char('Asset Number', size=6)
	asset_code = fields.Char('Asset Code', index=True)			
	notes = fields.Text('Notes')

	finance_state_color = fields.Selection(STATE_COLOR_SELECTION,related='finance_state_id.state_color', string="Color", readonly=True)
	warehouse_state_color = fields.Selection(STATE_COLOR_SELECTION,related='warehouse_state_id.state_color', string="Color", readonly=True)

	cost_center_id = fields.Many2one('analytic.code','Cost Center',domain=[('nd_id','=',1),('disabled_per_company','=',False)],required=False)
	to_be_processed = fields.Boolean("To be Processed")

	# image: all image fields are base64 encoded and PIL-supported
	image = fields.Binary("Photo", attachment=True,
		help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
	image_medium = fields.Binary("Medium-sized photo",
		compute='_compute_images', inverse='_inverse_image_medium', store=True, attachment=True,
		help="Medium-sized photo of the employee. It is automatically "\
		     "resized as a 128x128px image, with aspect ratio preserved. "\
		     "Use this field in form views or some kanban views.")
	image_small = fields.Binary("Small-sized photo",
		compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
		help="Small-sized photo of the employee. It is automatically "\
		     "resized as a 64x64px image, with aspect ratio preserved. "\
		     "Use this field anywhere a small image is required.")
	
	employee_id = fields.Many2one('hr.employee', 'Employee', domain=[('team','=','0')])
	asset_type = fields.Char(string='Type')
	make = fields.Char(string='Make')
	engine_number = fields.Char(string='Engine Number')
	chassis_number = fields.Char(string='Chassis Number')
	cost = fields.Float(string='Cost')
	depreciation = fields.Float(string='Depreciation')
	insured = fields.Selection([('yes','Yes'),('no','NO')], string="Insured")
	insurance_policy_number = fields.Char(string='Insurance Policy Number')
	insurance_policy_renewal_date = fields.Date(string='Insurance Policy Renewal Date')
	tracker = fields.Selection([('yes','Yes'),('no','NO')], string="Tracker")
	tracker_renewal_date = fields.Date(string='Tracker Renewal Date')
	token = fields.Selection([('yes','Yes'),('no','NO')], string="Token")
	token_renewal_date = fields.Date(string='Token Renewal Date')
	
	general_remarks = fields.Text(string='General Remarks')
	

	@api.model
	def create(self, vals):
		vals['asset_number'] = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('asset.number')
		asset= super(asset_asset, self).create(vals)
		return asset

	@api.depends('image')
	def _compute_images(self):
		for rec in self:
			rec.image_medium = tools.image_resize_image_medium(rec.image)
			rec.image_small = tools.image_resize_image_small(rec.image)

	def _inverse_image_medium(self):
		for rec in self:
			rec.image = tools.image_resize_image_big(rec.image_medium)

	def _inverse_image_small(self):
		for rec in self:
			rec.image = tools.image_resize_image_big(rec.image_small)


	_group_by_full = {
		'finance_state_id': _read_group_finance_state_ids,
		'warehouse_state_id': _read_group_warehouse_state_ids,
		'manufacture_state_id': _read_group_manufacture_state_ids,
		'maintenance_state_id': _read_group_maintenance_state_ids,
	}

class AccountAssetCategory(models.Model):
	_inherit = 'account.asset.category'

	account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True, domain=[('internal_type','=','other'), ('deprecated', '=', False)])
	account_depreciation_id = fields.Many2one('account.account', string='Depreciation Account', required=True, domain=[('internal_type','=','other'), ('deprecated', '=', False)])
	account_acc_depreciation_id = fields.Many2one('account.account', string='Acc. Depreciation Account', domain=[('internal_type','=','other'), ('deprecated', '=', False)])
    

class account_asset(models.Model):
	_inherit = 'account.asset.asset'

	asset_id = fields.Many2one('asset.asset', 'Asset', required=True)
	off_depreciated_value = fields.Float('Depreciated Value (Off)',digits=0)
	prev_deprecians = fields.Integer('Prev. Deprecians')
	code = fields.Char(string='Reference', size=32, readonly=True, states={'draft': [('readonly', False)]}, related='asset_id.asset_code')
	to_be_processed = fields.Boolean()
	
	@api.onchange('asset_id')
	def onchange_asset(self):
		return {'value': {'name': self.name}}

	@api.model
	def close_assets(self,nlimit=100):		
		assets = self.search([('state','=','open')],limit=nlimit)	
		for asset in assets:	
			if asset.currency_id.is_zero(asset.value_residual):
				asset.message_post(body=("Document closed."))
				asset.write({'state': 'close'})

	@api.model
	def validate_assets(self,nlimit=100):		
		assets = self.search([('state','=','draft'),('company_id','in',(3,4))],limit=nlimit)	
		for asset in assets:
			asset.compute_depreciation_board()	
			asset.validate()

	@api.one
	@api.depends('value', 'salvage_value', 'off_depreciated_value', 'depreciation_line_ids')
	def _amount_residual(self):
		total_amount = 0.0
		for line in self.depreciation_line_ids:
			if line.move_check:
				total_amount += line.amount
		self.value_residual = self.value - total_amount - self.salvage_value - self.off_depreciated_value

	def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date):
		amount = 0
		if sequence == undone_dotation_number:
			amount = residual_amount
		else:
			if self.method == 'linear':
				amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids)-self.prev_deprecians)
				if self.prorata and self.category_id.type == 'purchase':
					amount = amount_to_depr / self.method_number
					days = total_days - float(depreciation_date.strftime('%j'))
					if sequence == 1:
						amount = (amount_to_depr / self.method_number) / total_days * days
					elif sequence == undone_dotation_number:
						amount = (amount_to_depr / self.method_number) / total_days * (total_days - days)
			elif self.method == 'degressive':
				amount = residual_amount * self.method_progress_factor
				if self.prorata:
					days = total_days - float(depreciation_date.strftime('%j'))
					if sequence == 1:
						amount = (residual_amount * self.method_progress_factor) / total_days * days
					elif sequence == undone_dotation_number:
						amount = (residual_amount * self.method_progress_factor) / total_days * (total_days - days)
		return amount


	@api.multi
	def compute_depreciation_board(self):
		self.ensure_one()

		posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check)
		unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

		# Remove old unposted depreciation lines. We cannot use unlink() with One2many field
		commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

		if self.value_residual != 0.0:
			amount_to_depr = residual_amount = self.value_residual
			if self.prorata:
				depreciation_date = datetime.strptime(self._get_last_depreciation_date()[self.id], DF).date()
			else:
				# depreciation_date = 1st of January of purchase year
				asset_date = datetime.strptime(self.date, DF).date()
				# if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
				if posted_depreciation_line_ids and posted_depreciation_line_ids[0].depreciation_date:
					last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[0].depreciation_date, DF).date()
					depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period, day=31)
				else:
					depreciation_date = asset_date
			day = depreciation_date.day
			month = depreciation_date.month
			year = depreciation_date.year
			total_days = (year % 4) and 365 or 366

			undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
			for x in range(len(posted_depreciation_line_ids)+self.prev_deprecians, undone_dotation_number):
				sequence = x + 1
				amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
				amount = self.currency_id.round(amount)
				residual_amount -= amount
				vals = {
					'amount': amount,
					'asset_id': self.id,
					'sequence': sequence,
					'name': (self.code or '') + '/' + str(sequence),
					'remaining_value': residual_amount,
					'depreciated_value': self.value - (self.salvage_value + residual_amount),
					'depreciation_date': depreciation_date.strftime(DF),
				}
				commands.append((0, False, vals))
				# Considering Depr. Period as months
				depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period, day=31)
				day = depreciation_date.day
				month = depreciation_date.month
				year = depreciation_date.year

		self.write({'depreciation_line_ids': commands})

		return True
		
