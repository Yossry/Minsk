import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ReportPurchase(models.AbstractModel):
	_name = 'report.sos_uniform.report_purchase'
	_description = 'Purchase Report in Uniforms'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		categ_id = data['form']['categ_id'] and data['form']['categ_id'][0]
		
		purchases = self.env['stock.move'].search([('date', '>=', date_from),('date','<=',date_to),('product_id.product_tmpl_id.categ_id.id', '=',categ_id ),('location_dest_id', '=', 12)],order='date,product_id')
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_purchase')
		return  {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Purchases" : purchases or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
