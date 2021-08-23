import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class MonthWisePFReport(models.AbstractModel):
	_name = 'report.sos_provident_fund.month_wise_pf_report'
	_description = 'Monthly PF Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		res = []
		total = 0
		res.append({
			'jan' : 0,
			'feb' : 0,
			'mar' : 0,
			'apr' : 0,
			'may' : 0,
			'jun' : 0,
			'jul' : 0,
			'aug' : 0,
			'sep' : 0,
			'oct' : 0,
			'nov' : 0,
			'dec' : 0,
			'total' : 0,
		})
		self.env.cr.execute("""select to_char(date_from,'Mon-YY') as month_year,sum(total) as Total from guards_payslip_line where code='GPROF' and date_from >='2019-01-01' group by 1 order by  month_year""" )
		results = self.env.cr.dictfetchall()
		for result in results:
			if result['month_year'] == 'Jan-19':
				res[0]['jan'] = abs(result['total'])
				total = total +  abs(result['total'])
			elif result['month_year'] == 'Feb-19':
				res[0]['feb'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Mar-19':
				res[0]['mar'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Apr-19':
				res[0]['apr'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'May-19':
				res[0]['may'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Jun-19':
				res[0]['jun'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Jul-19':
				res[0]['jul'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Aug-19':
				res[0]['aug'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Sep-19':
				res[0]['sep'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Oct-19':
				res[0]['oct'] = abs(result[total])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Noc-19':
				res[0]['nov'] = abs(result['total'])
				total = total + abs(result['total'])
			elif result['month_year'] == 'Dec-19':
				res[0]['dec'] = abs(result['total'])
				total = total + abs(result['total'])
			else:
				sa = 0
		res[0]['total'] = total

		report = self.env['ir.actions.report']._get_report_from_name('sos_provident_fund.month_wise_pf_report')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			'rep_data' : res,
			"get_date_formate" : self.get_date_formate,
		}