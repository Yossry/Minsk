import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
from openerp import models, fields, api, _

class expire_docs_wizard(models.TransientModel):
	_name = 'expire.docs.wizard'
	_description = 'Employee Docs Expiry Wizard'
	
	status = fields.Selection([('expired','Expired'),('near_to_expired','Near To Expire'),('all','All')],'Status',default='all')
	
	def _build_contexts(self, data):
		result = {}
		result['status'] = data['form']['status'] or False
		return result

	@api.multi
	def print_report(self):
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})
		return self.env.ref('hr_ext.report_expired_docs').with_context(landscape=True).report_action(self, data=data, config=False)
