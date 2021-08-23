
from odoo import api, models, fields, _
from odoo.tools import config
from odoo import exceptions
from odoo.osv import orm
import pdb

DIMENSION_DUPLICATE_ERROR = _("Both {model1} and {model2} reference {dim}")
NO_MODEL_FOR_DIMENSION_ERROR = _("No model matches dimension {dim}")


def check_dimension_duplicate(models_by_dimension, dim_name, model_name):
	"""Used by analytic_dimension.sync_analytic_codes_action.
	Make sure that dim_name is not a key in models_by_dimension.
	If the value is present, that would indicate that two different models
	define dimensions with the same name so we can't decide which model
	we want to use to sync analytic codes.

	tl;dr Raises odoo.exceptions.ValidationError of dim_name is a key of models_by_dimension.

	:param models_by_dimension: dict, mapping from dimension names to
		model names.

	:param dim_name: str, name of a dimension

	:param mode_name: str, name of a model that references dim_name.

	:raises: odoo.exceptions.ValidationError
	"""
	if dim_name in models_by_dimension:
		model1 = model_name
		model2 = models_by_dimension[dim_name]
		raise exceptions.ValidationError(_(DIMENSION_DUPLICATE_ERROR).format(model1=model1, model2=model2, dim=dim_name))


def get_analytic_size():
	"""Return analytic size (from config)
	:return: an int (default to 5)
	"""
	#return int(config.get_misc('analytic', 'analytic_size', 5))
	return 10


class _dimension_meta(orm.MetaModel):

	def __new__(cls, name, bases, nmspc):
		
		size = get_analytic_size()
		for n in range(1, size + 1):
			nmspc['ns{}_id'.format(n)] = fields.One2many('analytic.structure','nd_id',"Generated Subset of Structures",domain=[('ordering', '=', n)],auto_join=True,)
		return super(_dimension_meta, cls).__new__(cls, name, bases, nmspc)


class AnalyticDimension(models.Model, metaclass = _dimension_meta):

	_name = 'analytic.dimension'
	_description = 'Analytic Dimension'

	name = fields.Char("Name",size=128,	translate=config.get_misc('analytic', 'translate', False),	required=True,)
	nc_ids = fields.One2many('analytic.code','nd_id',"Codes")
	ns_id = fields.One2many('analytic.structure','nd_id',"Structures")
	
	_sql_constraints = [
		('unique_name', 'unique(name)', u"Name must be unique"),
	]

	@api.multi
	def sync_analytic_codes_action(self):
		"""Create missing analytic codes"""
		registry = self.env.registry
		dimension_models = [(name, model) for name, model in registry.items() if getattr(model, '_dimension', None)]

		# Dimension name => model object
		models_by_dimension = {}
		# Dimension name => analytic.code m2o field name
		column_by_name = {}
		# Place dimension info into dicts for easy retrieval
		for model_name, model in dimension_models:
			dim_config = getattr(model, '_dimension')
			if isinstance(dim_config, dict):
				dim_name = dim_config.get('name')
				column_name = dim_config.get('column', 'analytic_id')
			else:
				dim_name = dim_config
				column_name = 'analytic_id'

			check_dimension_duplicate(models_by_dimension, dim_name, model_name)
			models_by_dimension[dim_name] = model_name
			column_by_name[dim_name] = column_name

		for record in self:
			dimension_name = record.name

			if dimension_name not in models_by_dimension:
				raise exceptions.ValidationError(_(NO_MODEL_FOR_DIMENSION_ERROR).format(dim=dimension_name))

			model_name = models_by_dimension[dimension_name]
			code_column = column_by_name[dimension_name]

			model_obj = self.env[model_name]

			# Look for records with missing analytic codes
			missing_code = model_obj.search([(code_column, '=', False)])
			# Create codes for those records using 'write' method
			# defined in MetaAnalytic.
			for dim_record in missing_code:
				dim_record.write({})
