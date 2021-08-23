
from odoo import SUPERUSER_ID
from odoo import fields, api
from odoo.osv import orm
from odoo.tools import config, frozendict
import math
import pdb

from odoo.addons.analytic_structure.analytic_dimension import (get_analytic_size)
			
class AddMethod(object):
	"""Utility decorator to add methods to an object or a class."""

	def __init__(self, obj):
		self.obj = obj

	def __call__(self, func):
		setattr(self.obj, func.__name__, func)
		return func

class MetaAnalytic(orm.MetaModel):
	"""Allow the model to use the classes of the analytic_structure module in a more streamlined way.

	The metaclass' behavior is specified by adding the following attributes:

	* _analytic: define the analytic structures to be used by the model.
	* _dimensions: bind an analytic dimension to the model.

	A description of the syntax expected for each attribute is available in the README file.

	Notes:
	* This metaclass may directly modify attributes that are used by OpenERP, specifically _inherits and the fields of the class.
	* New superclasses are used to define or override methods, in order to avoid interacting with the model's own method (re)definitions.
	"""
		
	def __new__(cls, name, bases, nmspc):
		analytic = nmspc.get('_analytic', {})
		para = nmspc.get('_para_analytic', {})
		dimension = nmspc.get('_dimension', {})

		defaults = nmspc.get('_defaults', None)
		if defaults is None:
			defaults = {}
			nmspc['_defaults'] = defaults

		orm_name = nmspc.get('_name', None)
		if orm_name is None:
			orm_name = nmspc.get('_inherit')

		# Analytic fields should be defined in the _analytic attribute.
		if analytic or para:
			bases = cls._setup_analytic_fields(analytic, para, defaults, orm_name, name, bases, nmspc)

		# The bound dimension should be defined in the _dimension attribute.
		if dimension:
			bases = cls._setup_bound_dimension(dimension, defaults, orm_name, name, bases, nmspc)

		return super(MetaAnalytic, cls).__new__(cls, name, bases, nmspc)

	def __init__(self, name, bases, nmspc):
		return super(MetaAnalytic, self).__init__(name, bases, nmspc)

	@classmethod
	def _setup_analytic_fields(cls, analytic, para, defaults, orm_name, name, bases, nmspc):
		"""Generate analytic and para-analytic fields on the model."""

		# If _analytic uses a shortcut, convert it into a prefix-model mapping.
		if analytic is True:
			analytic = {'a': orm_name.replace('.', '_')}
		elif isinstance(analytic, str):
			analytic = {'a': analytic}

		# Create a field that will be used for replacement in the view
		if analytic:
			nmspc['analytic_dimensions'] = fields.Char("Analytic Dimensions", compute=api.one(lambda self: (setattr(self, 'analytic_dimensions', ''))),	readonly=True,)

		col_pattern = '{pre}{n}_{suf}'
		size = get_analytic_size()
        
		# Generate the fields directly into the nmspc.
		all_analytic = []
		
		for prefix, model_name in analytic.items():
			# Analytic fields
			all_analytic.append((model_name, prefix, 'id'))
		
			nmspc['d_bin'] = fields.Char("Binary Dimension")
			nmspc['req_dimensions'] = fields.Boolean(default=True)

			for n in range(1, size + 1):
				col_name = col_pattern.format(pre=prefix, n=n, suf='id')
				col_hname = col_pattern.format(pre='H', n=n, suf='id')
				
				domain_field = 'nd_id.ns{n}_id.model_name'.format(n=n)
				nmspc[col_name] = fields.Many2one('analytic.code', "Generated Analytic Field",  
					domain=[(domain_field, '=', model_name), ('view_type', '=', False), ('disabled_per_company', '=', False), ],
					ondelete='restrict', track_visibility='onchange', index=True,)
				nmspc[col_hname] = fields.Integer(compute='_get_d_bin')

		for key, value in para.items():
			# Para-analytic fields
			prefix, suffix = key
			model_name = value['model']
			all_analytic.append((model_name, prefix, suffix))
			if suffix == 'id':
				raise ValueError("Para-analytic suffix cannot be 'id'")

			field_type = value['type']
			args = value['args']
			kwargs = value['kwargs']
			for n in range(1, size + 1):
				col_name = col_pattern.format(pre=prefix, n=n, suf=suffix)
				nmspc[col_name] = field_type(*args, **kwargs)
				if 'default' in value:
					defaults[col_name] = value['default']

		# In order to preserve inheritance and possible overrides, work on a
		# new class that inherits the given bases, then make our model class
		# inherit from this class.
		superclass_name = '_{name}_SuperAnalytic'.format(name=name)
		# Set _register to False in order to prevent its instantiation.
		superclass = type(superclass_name, bases, {'_register': False})
		
		@AddMethod(superclass)
		@api.onchange('account_id')
		def _onchange_account_id(self):		
			if self.account_id:
				dimensions = self.account_id.nd_ids			
				structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids)])
				used = [int(structure.ordering) for structure in structures]
			
				number = 0
				size = int(config.get_misc('analytic', 'analytic_size', 10))
				for n in range(1, size + 1):				
					if n in used:
						src_data = 1
						number += math.pow(2,n-1)
				self.d_bin = bin(int(number))[2:].zfill(10)
				if int(number):
					self.req_dimensions = True	
				else:
					self.req_dimensions = False
				
		
		@AddMethod(superclass)
		@api.one
		@api.depends('d_bin')
		def _get_d_bin(self):
			if self.d_bin:
				self.H10_id = int(self.d_bin[0:1])
				self.H9_id = int(self.d_bin[1:2])
				self.H8_id = int(self.d_bin[2:3])
				self.H7_id = int(self.d_bin[3:4])
				self.H6_id = int(self.d_bin[4:5])
				self.H5_id = int(self.d_bin[5:6])
				self.H4_id = int(self.d_bin[6:7])
				self.H3_id = int(self.d_bin[7:8])
				self.H2_id = int(self.d_bin[8:9])
				self.H1_id = int(self.d_bin[9:10])
		
		@AddMethod(superclass)
		@api.model
		def fields_get(self, allfields=None, attributes=None):
			"""Override this method to rename analytic fields."""			
			res = super(superclass, self).fields_get(allfields=allfields, attributes=attributes)
		
			analytic_osv = self.env['analytic.structure']
			for model_name, prefix, suffix in all_analytic:
				res = analytic_osv.analytic_fields_get(model_name, res, prefix, suffix)		
			return res		

		@AddMethod(superclass)
		@api.model
		def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
			"""Override this method to hide unused analytic fields."""
			res = super(superclass, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

			analytic_osv = self.env['analytic.structure']
			for model_name, prefix, suffix in all_analytic:
				res = analytic_osv.analytic_fields_view_get(model_name, res, prefix, suffix)
			return res

		@AddMethod(superclass)
		@api.model
		@api.returns(orm_name, lambda value: value.id)
		def create(self, vals, **kwargs):
			"""Performs analytic field validation"""
			res = super(superclass, self).create(vals, **kwargs)
			# Throws in case of error
			res._validate_analytic_fields(frozendict(analytic))
			return res

		@AddMethod(superclass)
		@api.multi
		def write(self, vals, **kwargs):
			"""Performs analytic field validation"""
			res = super(superclass, self).write(vals, **kwargs)
			# Throws in case of error
			self._validate_analytic_fields(frozendict(analytic))
			return res

		@AddMethod(superclass)
		@api.multi
		def _validate_analytic_fields(self, analytic):
			"""Validation function to validate analytic fields.
			The base implementation doesn't actually do anything.
			:param analytic: frozendict, analytic field parameters, such as
				   they would appear in the '_analytic' in the expanded
				   form, ie. as a prefix => model_name mapping.
			:raises: Validation error when applicable.
			"""
			pass	
		
		return (superclass,)

	@classmethod
	def _setup_bound_dimension(cls, dimension, defaults, orm_name, name, bases, nmspc):
		"""Bind a dimension to the model, creating a code for each record."""

		if dimension is True:
			dimension = {}
		elif isinstance(dimension, str):
			dimension = {'name': dimension}

		dimension_name = dimension.get('name', None)
		if dimension_name is None:
			dimension_name = nmspc.get('_description', False) or orm_name

		column = dimension.get('column', 'analytic_id')

		ref_module = dimension.get('ref_module', '')

		ref_id = dimension.get('ref_id', None)
		if ref_id is None:
			ref_id = orm_name.replace('.', '_') + "_analytic_dimension_id"

		# To use an inherited, renamed parent field, you have to give its name.
		sync_parent = dimension.get('sync_parent', False)
		if sync_parent is True:
			sync_parent = nmspc.get('_parent_name', 'parent_id')

		rel_name = dimension.get('rel_name', tuple())
		if rel_name is True:
			rel_name = u"Name"
		if isinstance(rel_name, str):
			rel_name = (rel_name, 'name')

		rel_code = dimension.get('rel_code', tuple())
		if rel_code is True:
			rel_code = u"Code"
		if isinstance(rel_code, str):
			rel_code = (rel_code, 'code')

		rel_description = dimension.get('rel_description', tuple())
		if rel_description is True:
			rel_description = u"Description"
		if isinstance(rel_description, str):
			rel_description = (rel_description, 'description')

		rel_active = dimension.get('rel_active', tuple())
		if rel_active is True:
			rel_active = u"Active"
		if isinstance(rel_active, str):
			rel_active = (rel_active, 'active')

		rel_view_type = dimension.get('rel_view_type', tuple())
		if rel_view_type is True:
			rel_view_type = u"View type"
		if isinstance(rel_view_type, str):
			rel_view_type = (rel_view_type, 'view_type')

		rel_disabled_per_company = dimension.get(
			'rel_disabled_per_company', tuple()
		)
		if rel_disabled_per_company is True:
			rel_disabled_per_company = u"Disabled in my company"
		if isinstance(rel_disabled_per_company, str):
			rel_disabled_per_company = (
				rel_disabled_per_company, 'disabled_per_company'
			)

		# By default, only use inherits if we can be sure there is no conflict
		# on the required fields 'name' and 'nd_id'.
		# There can still be conflicts on analytic_code's optional fields.
		use_inherits = dimension.get('use_inherits', None)
		if use_inherits is None:
			use_inherits = not (
				any(field in nmspc for field in ('name', 'nd_id')) or
				nmspc.get('_inherits', False) or
				nmspc.get('_inherit', False)
			)

		use_code_name_methods = dimension.get('use_code_name_methods', False)

		code_ref_ids = dimension.get('code_ref_ids', False)
		if code_ref_ids is True:
			code_ref_ids = ref_id

		code_ref_module = dimension.get('code_ref_module', '')

		if use_inherits:			
			inherits = nmspc.get('_inherits', {})
			inherits['analytic.code'] = column
			nmspc['_inherits'] = inherits
			
			if column not in nmspc:
				nmspc[column] = fields.Many2one('analytic.code', "Bound Analytic Code",	auto_join=True, index=True, ondelete="cascade", required=True)
		# Default column for the underlying analytic code.
		else:
			if column not in nmspc:
				nmspc[column] = fields.Many2one('analytic.code', "Bound Analytic Code",	required=True, ondelete='restrict')

		rel_cols = [
			cols for cols in [
				rel_name + ('name', 'Char', True, ''),
				rel_code + ('code', 'Char', False, ''),
				rel_description + ('description', 'Char', False, ''),
				rel_active + ('active', 'Boolean', False, True),
				rel_view_type + ('view_type', 'Boolean', False, False),
			] if len(cols) == 6
		]

		if rel_cols:
			# NOT a method nor a class member. 'self' is the analytic_code OSV.
			def _record_from_code_id(self, cr, uid, ids, context=None):
				"""Get the entries to update from the modified codes."""
				osv = self.pool.get(orm_name)
				domain = [(column, 'in', ids)]
				return osv.search(cr, uid, domain, context=context)

			for string, model_col, code_col, dtype, req, default in rel_cols:
				nmspc[model_col] = getattr(fields, dtype)(
					string=string,
					related=".".join([column, code_col]),
					relation="analytic.code",
					required=req,
					ondelete='restrict',
					store=True
				)
				if model_col not in defaults:
					defaults[model_col] = default

		# In order to preserve inheritance and possible overrides, work on a
		# new class that inherits the given bases, then make our model class
		# inherit from this class.
		superclass_name = '_{name}_SuperDimension'.format(name=name)
		# Set _register to False in order to prevent its instantiation.
		superclass = type(superclass_name, bases, {'_register': False})

		# We must keep the old api here !!!!!!!
		# If we switch to the new, the method is call through a wrapper
		# then, 'self' is a !#@*ing (!) object of the same type of __cls__
		# but totally temporary.
		# We don't want that cause we set _bound_dimension_id.
		# Keep the old api until we fix all this module.
		
		@AddMethod(superclass)
		def _get_bound_dimension_id(self):
				
			ref_module = self._dimension.get('ref_module', '')

			ref_id = self._dimension.get('ref_id', None)
			if ref_id is None:
				ref_id = self._name.replace('.', '_') + "_analytic_dimension_id"
			
			data_osv = self.env['ir.model.data']
			nd_id = data_osv.sudo().get_object_reference(ref_module, ref_id)[1]
			return nd_id


		@AddMethod(superclass)
		def _setup_complete(self):
			"""Load or create the analytic dimension bound to the model."""
			super(superclass, self)._setup_complete()
		
			data_osv = self.env['ir.model.data']
			try:
				self._bound_dimension_id = data_osv.sudo().get_object_reference(ref_module, ref_id)[1]
			except ValueError:
				vals = {'name': dimension_name, 'validated': True}
#SARFRAZ#				#self._bound_dimension_id = data_osv.sudo()._update('analytic.dimension', ref_module, vals, xml_id=ref_id, noupdate=True)

		if code_ref_ids:
			prefix = config.get_misc('analytic', 'code_ref_prefix', False)

			# This function is called as a method and can be overridden.
			@AddMethod(superclass)
			def _generate_code_ref_id(self, cr, uid, ids, context=None):
				data_osv = self.pool['ir.model.data']
				records = self.browse(cr, uid, ids, context=None)
				if not isinstance(records, list):
					records = [records]

				for record in records:
					code = record[column]
					code_ref_id_builder = [prefix] if prefix else []
					if 'company_id' in record and record.company_id:
						code_ref_id_builder.append(record.company_id.code)
					code_ref_id_builder.append('ANC')
					code_ref_id_builder.append(code_ref_ids)
					code_ref_id_builder.append(code.name)

					vals = {
						'name': "_".join(code_ref_id_builder),
						'module': code_ref_module,
						'model': 'analytic.code',
						'res_id': code.id,
					}
					data_osv.create(cr, uid, vals, context=context)

		@AddMethod(superclass)
		@api.model
		@api.returns(orm_name, lambda a: a.id)
		def create(self, vals, **kwargs):
			"""Create the analytic code."""
			
			code_vals = {}			
			if sync_parent:
				cp = self._get_code_parent(vals)
				if cp is not None:
					code_vals['code_parent_id'] = cp

			# Direct changes to the 'bound analytic code' field are ignored unless the 'force_code_id' context key is passed as True.
			force_code_id = vals.pop(column, False)

			# Will be set if a new code is created
			new_code = False

			if self._context and self._context.get('force_code_id', False):
				self._force_code(force_code_id, code_vals)
				vals[column] = force_code_id

			else:
				if use_inherits:
					code_vals.update(vals)
				else:
					
					if self._name == 'sale.order' and not vals.get('name',False):
						if 'company_id' in vals:
							vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
						else:
							vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
					
					code_vals['name'] = vals.get('name')
					code_vals['code'] = vals.get('code')
					
				# OpenERP bug: related fields do not work properly on creation.
				for rel in rel_cols:
					model_col, code_col = rel[1:3]
					if model_col in vals:
						code_vals[code_col] = vals[model_col]
					elif model_col in self._defaults:
						code_vals[code_col] = self._defaults[model_col]

				# We have to create the code separately, even with inherits.
				code_osv = self.env['analytic.code']
				code_vals['nd_id'] = self._get_bound_dimension_id()
				new_code = code_osv.create(code_vals)
				vals[column] = new_code.id
				
			res = super(superclass, self).create(vals, **kwargs)

			if code_ref_ids:
				self._generate_code_ref_id(res)

			if new_code:
				new_code.write({'origin_id': '{},{}'.format(self._name, res.id),})

			return res


		@AddMethod(superclass)
		@api.one
		def write(self, vals, **kwargs):
			"""Update the analytic code's name if it is not inherited, and its parent code if parent-child relations are synchronized. """
		
			code_vals = {}
			if sync_parent:
				cp = self._get_code_parent(vals)
				if cp is not None:
					code_vals['code_parent_id'] = cp

			# Direct changes to the 'bound analytic code' field are ignored unless the 'force_code_id' context key is passed as True.
			force_code_id = vals.pop(column, False)

			if self._context and self._context.get('force_code_id', False):
				self._force_code(force_code_id, code_vals)
				vals[column] = force_code_id

			elif use_inherits:
				vals.update(code_vals)

			else:					
				name_col = rel_name[1] if rel_name else 'name'
				if name_col in vals:
					code_vals['name'] = vals[name_col]

				code_col = rel_code[1] if rel_code else 'code'
				if code_col in vals:
					code_vals['code'] = vals[code_col]

				analytic_code = getattr(self, column)

				# If updating a single record with no code, create it.
				if not analytic_code:					
					code_vals['nd_id'] = self._get_bound_dimension_id()
					if 'name' not in code_vals:
						code_vals['name'] = self[name_col]  #self.read(cr, uid, new, [name_col], context=context)[name_col]

					if 'code' not in code_vals:
						code_vals['code'] = self[code_col]  #self.read(cr, uid, new, [code_col], context=context)[code_col]
	
					code_vals['origin_id'] = '{},{}'.format(self._name, self.id)					
					vals[column] = self.env['analytic.code'].create(code_vals).id
				elif code_vals:
					analytic_code.write(code_vals)


			res = super(superclass, self).write(vals, **kwargs)

			if code_ref_ids and analytic_code:
				self._generate_code_ref_id()

			return res

			
		@AddMethod(superclass)
		def unlink(self, **kwargs):
			"""When removing this object, remove all associated analytic codes referenced by this object.
			Note: the method will fail if the code is referenced by any other object due to the RESTRICT constraint. That is the intended behavior.
			"""
			code_obj = self.env['analytic.code']

			# Find all related codes
			code_ids = [record[column] for record in self]
			res = super(superclass, self).unlink()

			for code_id in code_ids:
				code_id.unlink(**kwargs)
			return res
			

		@AddMethod(superclass)
		def _force_code(self, cr, uid, force_code_id, code_vals, context=None):

			code_osv = self.pool['analytic.code']

			if not force_code_id:
				raise ValueError("An analytic code ID MUST be specified if the force_code_id key is enabled in the context")
			force_code_dim = code_osv.read(cr, uid, force_code_id, ['nd_id'], context=context)['nd_id'][0]
			if force_code_dim != self._bound_dimension_id:
				raise ValueError("If specified, codes must belong to the bound analytic dimension {}".format(dimension_name))
			if code_vals:
				code_osv.write(cr, uid, force_code_id, code_vals, context=context)

		if sync_parent:
			# This function is called as a method and can be overridden.
			@AddMethod(superclass)
			def _get_code_parent(self, cr, uid, vals, context=None):
				"""If parent_id is in the submitted values, return the analytic
				code of this parent, to be used as the child's code's parent.
				"""
				parent_id = vals.get(sync_parent, None)
				if parent_id is not None:
					if parent_id:
						res = self.read(cr, uid, parent_id, [column], context=context)[column]
						return res[0] if res else False
					else:
						return False
				return None

		if use_code_name_methods:

			@AddMethod(superclass)
			def name_get(self, cr, uid, ids, context=None):
				"""Return the analytic code's name."""

				code_osv = self.pool.get('analytic.code')
				code_reads = self.read(cr, uid, ids, [column], context=context)
				c2m = {  # Code IDs to model IDs
					code_read[column][0]: code_read['id'] for code_read in code_reads if code_read[column] is not False
				}
				names = code_osv.name_get(cr, uid, c2m.keys(), context=context)
				return [(c2m[cid], name) for cid, name in names if cid in c2m]

			@AddMethod(superclass)
			def name_search(self, cr, uid, name, args=None, operator='ilike', context=None,	limit=100):
				"""Return the records whose analytic code matches the name."""

				code_osv = self.pool.get('analytic.code')
				args.append(('nd_id', '=', self._bound_dimension_id))
				names = code_osv.name_search(cr, uid, name, args, operator, context, limit)
				if not names:
					return []
				dom = [(column, 'in', zip(*names)[0])]
				ids = self.search(cr, uid, dom, context=context)
				code_reads = self.read(cr, uid, ids, [column], context=context)
				c2m = {  # Code IDs to model IDs
					code_read[column][0]: code_read['id'] for code_read in code_reads if code_read[column] is not False
				}
				return [
					(c2m[cid], cname) for cid, cname in names if cid in c2m
				]

		return (superclass,)
