import pdb
import time
import re
from datetime import datetime
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo import tools


class format_address(object):
		
	@api.model
	def fields_view_get_address(self, arch):
		fmt = "%(street)s\n%(street2)s\n%(city)s %(zip)s\n%(country_name)s"
		layouts = {
			'%(city)s \n%(zip)s': """
				<div class="address_format">
					<field name="city" placeholder="City" style="width: 50%%"/>                    
					<br/>
					<field name="zip" placeholder="ZIP"/>
				</div>
			""",
			'%(zip)s %(city)s': """
				<div class="address_format">
					<field name="zip" placeholder="ZIP" style="width: 40%%"/>
					<field name="city" placeholder="City" style="width: 57%%"/>                    
				</div>
			""",
			'%(city)s\n%(zip)s': """
				<div class="address_format">
					<field name="city" placeholder="City"/>                    
					<field name="zip" placeholder="ZIP"/>
				</div>
			"""
		}
		for k,v in layouts.items():
			if fmt and (k in fmt):
				doc = etree.fromstring(arch)
				for node in doc.xpath("//div[@class='address_format']"):
					tree = etree.fromstring(v)
					node.getparent().replace(node, tree)
				arch = etree.tostring(doc)
				break
			return arch
		

class sos_partner_address_category(models.Model):
	_description = 'Partner Address Categories'
	_name = 'sos.partneraddress.category'
	_parent_store = True
	_parent_order = 'name'
	_order = 'parent_left,name'
	
	name =  fields.Char('Category Name', required=True, size=64, translate=True)
	parent_id = fields.Many2one('sos.partneraddress.category', 'Parent Category', index=True, ondelete='cascade')
	complete_name = fields.Char(compute='_name_get_fnc', string='Full Name')
	child_ids = fields.One2many('sos.partneraddress.category', 'parent_id', 'Child Categories')
	active = fields.Boolean('Active', default=1,help="The active field allows you to hide the category without removing it.")
	parent_left = fields.Integer('Left parent', index=True)
	parent_right = fields.Integer('Right parent', index=True)
	partner_ids = fields.Many2many('sos.partneraddress', id1='category_id', id2='partneraddress_id', string='Contacts')
	parent_path = fields.Char(index=True)
	
	@api.constrains('parent_id')
	def _check_parent_id(self):
		if not self._check_recursion():
			raise ValidationError(_('Error ! You can not create recursive tags.'))
	
	@api.multi
	def name_get(self):
		#if self._context.get('sos_partneraddress_display') == 'short':
		#	return super(sos_partner_address_category, self).name_get()
		
		res = []
		for category in self:
			names = []
			current = category
			while current:
				names.append(current.name)
				current = current.parent_id
			res.append((category.id, ' / '.join(reversed(names))))	
		return res
	
	@api.multi
	def _name_get_fnc(self, field_name, arg):
		return dict(self.name_get())

	

class SOSPartnerAddress(models.Model):	
	_description = "SOS Partner Address"		
	_name = 'sos.partneraddress'
	_order = 'type, name'
	
	@api.onchange('type')
	def onchange_type(self):		
		color = 0
		if self.type:
			if self.type == 'default':
				color = 1
			elif self.type == 'home':
				color = 2
			elif self.type == 'work':
				self.color = 3
			elif self.type == 'other':
				self.color = 4
			elif self.type == 'permanent':
				color = 5
			elif self.type == 'headoffice':
				color = 6
				
		return {'value': {'color': color}}
	

	name = fields.Char('Contact Name', size=64, index=1)
	fathername = fields.Char('Father Name', size=64)
	cnic = fields.Char('CNIC', size=20, index=1)
	parent_id = fields.Many2one('sos.partneraddress', 'Guardian', ondelete='set null', index=True)
	child_ids = fields.One2many('sos.partneraddress', 'parent_id', 'Contacts')
	type = fields.Selection( [ ('default','Default'),('home','Home'), ('work','Work'), ('other','Other'),('permanent','Permanent'),('headoffice','Head Office') ],'Address Type', default='default',help="Used to select automatically the right address according to the context.")
	profession = fields.Char('Profession', size=128)
	street = fields.Char('Street', size=128)
	street2 = fields.Char('Street2', size=128)
	zip = fields.Char('Zip', change_default=True, size=24)
	city = fields.Many2one('sos.city', 'City')
	country_id = fields.Many2one('res.country', 'Country',default=179)
	email = fields.Char('Email', size=240)
	phone = fields.Char('Phone', size=64)
	mobile = fields.Char('Mobile', size=64)
	fax = fields.Char('Fax', size=64)
	birthdate = fields.Char('Birthdate', size=64)
	active = fields.Boolean('Active', default=1,help='Uncheck the active field to hide the contact.')
	color = fields.Integer('Color Index',default=1)
	# during update
	sos_category_ids = fields.Many2many('sos.partneraddress.category', 'partner_category_rel',id1='partneraddress_id', id2='category_id', string='Tags')
	
	guard_id = fields.Many2one('hr.guard','Guard')
	employee_id = fields.Many2one('hr.employee','Employee')
	post_id = fields.Many2one('sos.post','Post')
	
	 # image: all image fields are base64 encoded and PIL-supported
	image = fields.Binary("Photo", attachment=True, help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
	image_medium = fields.Binary("Medium-sized photo", compute='_compute_images', inverse='_inverse_image_medium', store=True, attachment=True, 
		help="Medium-sized photo of the employee. It is automatically resized as a 128x128px image, with aspect ratio preserved. Use this field in form views or some kanban views.")
	image_small = fields.Binary("Small-sized photo", compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
		help="Small-sized photo of the employee. It is automatically resized as a 64x64px image, with aspect ratio preserved. Use this field anywhere a small image is required.")
	
	@api.multi
	@api.depends('image')
	def _compute_images(self):
		for rec in self:
		    rec.image_medium = tools.image_resize_image_medium(rec.image)
		    rec.image_small = tools.image_resize_image_small(rec.image)
	
	@api.multi
	def _inverse_image_medium(self):
		for rec in self:
		    rec.image = tools.image_resize_image_big(rec.image_medium)
	
	@api.multi
	def _inverse_image_small(self):
		for rec in self:
		    rec.image = tools.image_resize_image_big(rec.image_small)

	def _get_default_image(self):
		image_path = get_module_resource('sos', 'static/src/img', 'default_image.png')
		return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))


