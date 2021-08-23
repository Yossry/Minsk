
from odoo.osv import expression
from odoo import models, fields, api
from odoo.tools import config
import pdb

class AnalyticCode(models.Model):
	_name = 'analytic.code'
	_description = 'Analytic Code'

	_parent_name = 'code_parent_id'
	_parent_store = True
	_parent_order = 'name'
	_order = 'code'

	@api.depends('blacklist_ids')
	def _read_disabled_per_company(self):
		"""Mark the code as disabled when it is in the blacklist (depending on the current user's company)."""

		company_id = self.env.user.company_id.id

		for anc in self:
			blacklist = (company.id for company in anc.blacklist_ids)
			anc.disabled_per_company = company_id in blacklist

	def _write_disabled_per_company(self):
		"""Update the blacklist depending on the current user's company."""

		company_id = self.env.user.company_id.id

		for anc in self:
			blacklist = (company.id for company in anc.blacklist_ids)

			to_write = None
			if anc.disabled_per_company and company_id not in blacklist:
				to_write = [(4, company_id)]  # Link.
			elif not anc.disabled_per_company and company_id in blacklist:
				to_write = [(3, company_id)]  # Unlink.

			if to_write:
				anc.write({'blacklist_ids': to_write})

		return True

	def _search_disabled_per_company(self, operator, value):
		"""Update the domain to take the blacklist into account (depending on the current user's company)."""

		company_id = self.env.user.company_id.id

		# We assume the criterion was "disabled_per_company = False".
		dom = ['|',('blacklist_ids', '=', False),('blacklist_ids', '!=', company_id),]
		if value is True:
		    dom = ['!'] + dom
		return dom

	def _get_origin_id_selection(self):
		"""Looks up the list of models that define dimensions"""
		registry = self.env.registry
		models = [model for name, model in registry.items() if getattr(model, '_dimension', False)]

		res = [(model._name, model._description or model._name) for model in models]
		return res

	name = fields.Char("Name",size=128,translate=config.get_misc('analytic', 'translate', False),required=True,)
	code = fields.Char("Code",size=16,translate=config.get_misc('analytic', 'translate', False))
	nd_id = fields.Many2one('analytic.dimension',string="Dimension",ondelete='cascade',	required=True,)
	origin_id = fields.Reference(_get_origin_id_selection,string="Original Object",	help="The object that created this code",ondelete='cascade',)

	active = fields.Boolean("Active",help=("Determines whether an analytic code is in the referential."),default=lambda *a: True)
	view_type = fields.Boolean("View type",	help=("Determines whether an analytic code is not selectable (but still in the referential)."),	default=lambda *a: False)
	blacklist_ids = fields.Many2many('res.company',	'analytic_code_company_rel','code_id','company_id',"Blacklist",	help=u"Companies the code is hidden in.",)
	disabled_per_company = fields.Boolean(string="Disable in my company",compute=_read_disabled_per_company, inverse=_write_disabled_per_company, search=_search_disabled_per_company,
		help=("Determines whether an analytic code is disabled for the current company."),	default=lambda *a: False)

	nd_name = fields.Char(related='nd_id.name',	string="Dimension Name",store=False)
	description = fields.Char("Description",size=512,translate=config.get_misc('analytic', 'translate', False),)
	code_parent_id = fields.Many2one('analytic.code',"Parent Code",	index=True,ondelete='restrict',)
	child_ids = fields.One2many('analytic.code','code_parent_id',"Child Codes",)
	parent_left = fields.Integer("Left parent", index=True)
	parent_right = fields.Integer("Right parent", index=True)
	parent_path = fields.Char(index=True)

	_constraints = [
		# very useful base class constraint
		(
			models.Model._check_recursion,"Error ! You can not create recursive analytic codes.", ['parent_id']
		),
	]

	@api.multi
	def name_get(self):
		res = []
		for rec in self:
			name = (rec.code or ' ') + '-' + (rec.name or ' ')
			res += [(rec.id, name)]
		return res
    
	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=100):
		args = args or []
		connector = '|'
		if operator in expression.NEGATIVE_TERM_OPERATORS:
			connector = '&'
		recs = self.search([connector, ('code', operator, name), ('name', operator, name)] + args, limit=limit)
		return recs.name_get()
		

	
	

