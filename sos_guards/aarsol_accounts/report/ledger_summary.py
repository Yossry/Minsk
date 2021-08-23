import pdb
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from pytz import timezone
from odoo import api, models

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')



class LedgerSummary(models.AbstractModel):
	_name = 'report.aarsol_accounts.ledger_summary'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%B %Y')

	def format_field_name(self, ordering, prefix='a', suffix='id'):		
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)

	@api.model
	def get_report_values(self, docsid, data=None):			
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		date_start = data['form']['date_start']
		account_id = data['form']['account_id']
		dimension_id = data['form']['dimension_id']
		display_att = data['form']['display_att']
		interval_count = data['form']['interval_count']
		interval = data['form']['interval']

		if display_att == 'balance':
			display_att = 'debit - credit'

		if display_att == 'cbalance':
			display_att = 'credit - debit'

		an_structure = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',dimension_id[0])])
		dst_field_name = self.format_field_name(an_structure.ordering, 'a', 'id')

		months = []
		sql_param = []
		records = []

		for num in range(0,interval_count):				
			months.append((datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=+num,day=1)).strftime('%b-%y'))
			sql_param.append((datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=+num,day=1)).strftime('%Y-%m-%d'))
			sql_param.append((datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=+num,day=31)).strftime('%Y-%m-%d'))
		
		months.append("Totals")
		
		sql_param.append((datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(day=1)).strftime('%Y-%m-%d'))
		sql_param.append((datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=+(interval_count-1),day=31)).strftime('%Y-%m-%d'))	
		sql_param.append(account_id[0])

		sql = " select " 
		for i in range(0,interval_count):
			sql += "sum(case when date between %s and %s then " + display_att + " end),"
		sql += "sum(case when date between %s and %s then " + display_att + " end) from account_move_line where account_id = %s"
	
		self._cr.execute(sql,tuple(sql_param))
		recs = self._cr.fetchall()
		rec = recs[0]

		record = {}
		lst = list(rec)
		record['total'] = lst.pop()
		record['cols'] = tuple(lst)

		diff = [0]
		for j in range(1,interval_count):
			diff.append((rec[j] or 0)-(rec[j-1] or 0))
		record['diff'] = tuple(diff)

		records.append(record)
	

		sql = "select " + dst_field_name + " as dimension, "
		for i in range(0,interval_count):
			sql += "sum(case when date between %s and %s then " + display_att + " end),"
		sql += "sum(case when date between %s and %s then " + display_att + " end) from account_move_line where account_id = %s group by " + dst_field_name

		self._cr.execute(sql,tuple(sql_param))
		recs = self._cr.fetchall()

		for rec in recs:
			record = {}
			lst = list(rec)
			dimansion_code = lst.pop(0) 
			if dimansion_code:				
				record['dimension'] = self.env['analytic.code'].browse(dimansion_code).name
			else:
				record['dimension'] = 'Un-Defined'
				
			record['total'] = lst.pop()
			record['cols'] = tuple(lst)

			diff = [0]
			for j in range(2,interval_count+1):
				diff.append((rec[j] or 0)-(rec[j-1] or 0))
			record['diff'] = tuple(diff)

			records.append(record)

		
		report = self.env['ir.actions.report']._get_report_from_name('aarsol_accounts.ledger_summary')
		#partners = self.env['res.partner'].browse(data['form']['partner_id'][0])
		
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'docs': self,
			'data': data['form'],			
			'time': time,
			'get_date_formate' : self.get_date_formate,
			'months': months,
			'lines': records,		
		}				
		return docargs
	
	
	#***** Excel Report *****#
	@api.multi
	def make_excel(self, data):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		recs = self.get_report_values(None,data)
		
		#***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Ledger Summary Report")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header2 = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz right")
		style_table_totals2 = xlwt.easyxf("font:height 150; font: name Liberation Sans ,color black; align: horiz right")
		
		
		table_header = ['Sr','Dimension']
		header_length = len(table_header)
		for month in recs['months']:
			table_header.append(month)
		
		worksheet.write_merge(0, 1, 0,header_length-1,"Ledger Summary Report", style= style_table_header)
		row = 2
		col = 0
		
		#***** Table Heading *****#
		for i in range(header_length):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
		#Col Widht
		w_col = 0
		worksheet.col(w_col).width = 256*10
		w_col +=1 
		worksheet.col(w_col).width = 256*25
		w_col +=1
		
		
		i = 0
		#***** Table Data *****#
		for line in recs['lines']:
			row += 1
			col = 0
			
			#First Row (Totals Row)
			if i == 0: 
				worksheet.write_merge(row,row,0,1,'Totals', style=style_table_header)
				col =2
				
				for num in line['cols']:
					if not num == None or False:
						worksheet.write(row,col,format(abs(num),'.2f' or 0.00), style=style_table_totals)
						col +=1
					if num == None:
						worksheet.write(row,col,'-', style=style_table_totals)
						col +=1				
				
				worksheet.write(row,col,format(line.get('total'),'.2f' or 0.00), style=style_table_totals)
				row += 1
				col = 0
			
			#Data Row
			if i > 0:
				worksheet.write(row,col,i, style=style_table_totals2)
				col +=1
				worksheet.write(row,col,line.get('dimension'),style=style_table_totals2)
				col +=1
				
				for num in line['cols']:
					if not num == None or False:
						worksheet.write(row,col,format(abs(num),'.2f' or 0.00), style=style_table_totals2)
						col +=1
					if num == None:
						worksheet.write(row,col,'-', style=style_table_totals)
						col +=1
				
				if line.get('total'):
					total = line.get('total')
				else:
					total = 0
						
				worksheet.write(row,col,format(total,'.2f' or 0.00), style=style_table_totals2)
				row += 1
				col = 0
				
			
			#Difference Row			
			worksheet.write_merge(row,row,0,1,'Difference', style=style_table_totals2)
			col =2
			for num in line['diff']:		
				if not num == None or False:
					worksheet.write(row,col,format(abs(num),'.2f' or 0.00), style=style_table_totals2)
					col +=1
				if num == None:
					worksheet.write(row,col,'-', style=style_table_totals2)
					col +=1
				
			i +=1 		
		
		file_data = io.BytesIO()		
		workbook.save(file_data)		
		return file_data.getvalue()			
			
