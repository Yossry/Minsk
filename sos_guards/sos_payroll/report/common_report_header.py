from odoo import pooler
from odoo.tools.translate import _

class common_report_header(object):    

	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('date_from', False):
			return data['form']['date_from']
		return ''

	def _get_target_move(self, data):
		if data.get('form', False) and data['form'].get('target_move', False):
			if data['form']['target_move'] == 'all':
				return _('All Entries')
			return _('All Posted Entries')
		return ''

	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''
        
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return self._translate('Date')
		return self._translate('No Filters')    
    

