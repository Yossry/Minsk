import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class PostsAddressReport(models.AbstractModel):
	_name = 'report.sos.report_postsaddress'
	_description = 'Post Address Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		city_id = data['form']['city_id'] and data['form']['city_id'][0]
		recs = self.env['sos.post'].search([('active','=',True),('center_id', '=', center_id),('postcity_id', '=', city_id)],order='name')
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_postsaddress')
		
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Posts' :recs or False,
			'get_date_formate' : self.get_date_formate,
		}
	
