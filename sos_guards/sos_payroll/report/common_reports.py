import pdb
import common_report_header
from odoo.osv import osv
from odoo.tools.translate import _


class CommonReportHeaderWebkit():
    

	####################From getter helper #####################################
	def _get_posts_br(self, data):
		return self._get_info(data, 'post_ids', 'sos.post')
		
	def _get_guards_br(self, data):
		return self._get_info(data, 'guard_ids', 'hr.employee')
		
	def _get_project_br(self, data):
		return self._get_info(data, 'project_ids', 'sos.project')	

	def _get_arms_br(self, data):
		return self._get_info(data, 'arm_ids', 'sos.arms')

	def _get_info(self, data, field, model):
		info = data.get('form', {}).get(field)
		if info:
			return self.pool.get(model).browse(self.cursor, self.uid, info)
		return False
    
	def _get_filter(self, data):
		return self._get_form_param('filter', data)

	def _get_target_move(self, data):
		return self._get_form_param('target_move', data)  

	def _get_date_from(self, data):
		return self._get_form_param('date_from', data)

	def _get_date_to(self, data):
		return self._get_form_param('date_to', data)

	def _get_form_param(self, param, data, default=False):
		return data.get('form', {}).get(param, default)

	def get_all_accounts(self, account_ids, context=None):       
		context = context or {}
		accounts = []
		if not isinstance(account_ids, list):
			account_ids = [account_ids]
		acc_obj = self.pool.get('account.account')
		for account_id in account_ids:
			accounts.append(account_id)
		
		res_ids = list(set(accounts))
		return res_ids

	
