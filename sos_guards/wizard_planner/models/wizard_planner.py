
from odoo import api, models, fields
from urllib.parse import urlencode
import pdb

class WizardPlanner(models.Model):

	_name = 'wizard.planner'
	_description = 'Wizard Planner'
	
	@api.model
	def _get_planner_application(self):
		return []

	name = fields.Char(string='Name', required=True)
	menu_id = fields.Many2one('ir.ui.menu', string='Menu')
	view_id = fields.Many2one('ir.ui.view', string='Template', required=True)
	progress = fields.Integer(string="Progress Percentage")
	# data field is used to store the data filled by user in planner(JSON Data)
	data = fields.Text(string="Data")
	tooltip_planner = fields.Html(string='Planner Tooltips', translate=True)
	rec_id = fields.Integer()
	rec_model = fields.Char()
	planner_application = fields.Selection('_get_planner_application', string='Planner Application', required=True)
	active = fields.Boolean(string="Active", default=True, 
		help="If the active field is set to False, it will allow you to hide the planner. This change requires a refresh of your page.")
	@api.model
	def render(self, template_id, planner_app, rec_id):		
		# prepare the planner data as per the planner application
		values = {
			'prepare_backend_url': self.prepare_backend_url,
			'is_module_installed': self.is_module_installed,
			'rec_id': rec_id,
		}
		#pdb.set_trace()
		#self.rec_id = rec_id
		planner_find_method_name = '_prepare_%s_wizard' % planner_app
		if hasattr(self, planner_find_method_name):
			values.update(getattr(self, planner_find_method_name)(rec_id)) # update the default value
		
		return self.env['ir.ui.view'].browse(template_id).render(values=values)

	@api.model
	def prepare_backend_url(self, action_xml_id, view_type='list', module_name=None):
		""" prepare the backend url to the given action, or to the given module view.
			:param action_xml_id : the xml id of the action to redirect to
			:param view_type : the view type to display when redirecting (form, kanban, list, ...)
			:param module_name : the name of the module to display (if action_xml_id is 'open_module_tree'), or
				                 to redirect to if the action is not found.
			:returns url : the url to the correct page
		"""
		params = dict(view_type=view_type)
		# setting the action
		action = self.env.ref(action_xml_id, False)
		if action:
			params['action'] = action.id
		else:
			params['model'] = 'ir.module.module'
		# setting the module
		if module_name:
			module = self.env['ir.module.module'].sudo().search([('name', '=', module_name)], limit=1)
			if module:
				params['id'] = module.id
			else:
				return "#show_enterprise"
		return "/web#%s" % (urlencode(params),)
	
	@api.model
	def is_module_installed(self, module_name=None):
		return module_name in self.env['ir.module.module']._installed()

	@api.model
	def get_planner_progress(self, planner_application):
		return self.search([('planner_application', '=', planner_application)]).progress
		
	
