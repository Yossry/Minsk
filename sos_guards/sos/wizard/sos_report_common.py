# -*- coding: utf-8 -*-

import time
from lxml import etree

from odoo.osv import fields, osv
from odoo.osv.orm import setup_modifiers
from odoo.tools.translate import _

class sos_common_report(osv.osv_memory):
	_name = "sos.common.report"
	_description = "SOS Common Report"

	def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
		res = {}
		if chart_account_id:
			company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
			res['value'] = {'company_id': company_id}
		return res

	_columns = {
		'post_ids': fields.many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts."""),                              
		'project_ids': fields.many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects."""),                              
		'center_ids': fields.many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers."""),                              
		'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
		'date_from': fields.date("Start Date"),
		'date_to': fields.date("End Date"),
		'target_move': fields.selection([('posted', 'All Posted Entries'),
			('all', 'All Entries'),
			], 'Target Moves'),
	} 
        
	def pre_print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])
		return data
        
	def onchange_filter(self, cr, uid, ids, filter='filter_no', context=None):
		res = {'value': {}}
		if filter == 'filter_no':
			res['value'] = {'date_from': False ,'date_to': False}
		if filter == 'filter_date':
			res['value'] = {'date_from': time.strftime('%Y-07-01'), 'date_to': time.strftime('%Y-%m-%d')}
		return res

	def _get_account(self, cr, uid, context=None):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
		return accounts and accounts[0] or False
    
	def _get_all_journal(self, cr, uid, context=None):
		return self.pool.get('account.journal').search(cr, uid ,[])

	_defaults = {
		'filter': 'filter_no',
		'target_move': 'posted',
	}

	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		
		if data['form']['filter'] == 'filter_date':
			result['date_from'] = data['form']['date_from']
			result['date_to'] = data['form']['date_to']
		return result

	def _print_report(self, cr, uid, ids, data, context=None):
		raise (_('Error!'), _('Not implemented.'))

	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		data = {}
		data['ids'] = context.get('active_ids', [])
		data['model'] = context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'filter',  'target_move'], context=context)[0]
		
		used_context = self._build_contexts(cr, uid, ids, data, context=context)
		data['form']['used_context'] = used_context
		return self._print_report(cr, uid, ids, data, context=context)

