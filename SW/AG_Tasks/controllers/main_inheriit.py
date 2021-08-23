# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http, fields, _
from ast import literal_eval
# import babel
# from dateutil.relativedelta import relativedelta
import itertools
import json
from odoo.http import request
from odoo.tools import float_round
from odoo.http import request
from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
# from ast import literal_eval
from odoo.addons.web.controllers.main import clean_action

class SaleTimesheetControllerinh(SaleTimesheetController):

	@http.route('/timesheet/plan', type='json', auth="user")
	def plan(self, domain):
		res = super(SaleTimesheetControllerinh,self).plan(domain)
		return res
	
	def _plan_prepare_values(self, projects):
		res = super(SaleTimesheetControllerinh,self)._plan_prepare_values(projects)
		
		return res
    
	def _plan_get_stat_button(self, projects):
		stat_buttonss = super(SaleTimesheetControllerinh,self)._plan_get_stat_button(projects)
		if len(projects) == 1:
			issue_id = request.env['issue.log'].search([('Project_name','=',projects.id)])        
			issue_lines = request.env['issue.log'].browse(issue_id).ids
			stat_buttonss.append({
				'name': _('Issue Log'),
				'count': len(issue_lines),
				'res_model': 'issue.log',
				'domain': [('Project_name','=',projects.id)],
				'context': {'default_Project_name': projects.id},
				'icon': 'fa fa-book',
			})
		return stat_buttonss

	
	@http.route('/timesheet/plan/action', type='json', auth="user")
	def plan_stat_button(self, domain=[], res_model='account.analytic.line', res_id=False):
		action = {
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'list',
            'domain': domain,
        }
		if res_model == 'project.project':
			view_form_id = request.env.ref('project.edit_project').id
			action = {
                'name': _('Project'),
                'type': 'ir.actions.act_window',
                'res_model': res_model,
                'view_mode': 'form',
                'view_type': 'form',
                'views': [[view_form_id, 'form']],
                'res_id': res_id,
            }
		elif res_model == 'account.analytic.line':
			ts_view_tree_id = request.env.ref('hr_timesheet.hr_timesheet_line_tree').id
			ts_view_form_id = request.env.ref('hr_timesheet.hr_timesheet_line_form').id
			action = {
				'name': _('Timesheets'),
				'type': 'ir.actions.act_window',
				'res_model': res_model,
				'view_mode': 'tree,form',
				'view_type': 'form',
				'views': [[ts_view_tree_id, 'list'], [ts_view_form_id, 'form']],
				'domain': domain,
			}
		elif res_model == 'project.task':
			action = request.env.ref('project.action_view_task').read()[0]
			action.update({
				'name': _('Tasks'),
				'domain': domain,
				'context': dict(request.env.context),  # erase original context to avoid default filter
			})
			# if only one project, add it in the context as default value
			tasks = request.env['project.task'].sudo().search(literal_eval(domain))
			if len(tasks.mapped('project_id')) == 1:
				action['context']['default_project_id'] = tasks.mapped('project_id')[0].id
		elif res_model == 'sale.order':
			action = clean_action(request.env.ref('sale.action_orders').read()[0])
			action['domain'] = domain
			action['context'] = {'create': False, 'edit': False, 'delete': False}  # No CRUD operation when coming from overview
		elif res_model == 'account.invoice':
			action = clean_action(request.env.ref('account.action_invoice_tree1').read()[0])
			action['domain'] = domain
			action['context'] = {'create': False, 'delete': False}  # only edition of invoice from overview

		elif res_model == 'issue.log':
			action = clean_action(request.env.ref('AG_Tasks.action_issue_log_cus').read()[0])
			action['domain'] = domain
			action['context'] = {'create': True, 'edit': True, 'delete': False}
		return action