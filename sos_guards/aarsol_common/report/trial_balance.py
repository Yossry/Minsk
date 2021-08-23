import pdb
import time
from itertools import groupby
from operator import itemgetter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from pytz import timezone
from odoo import api, models
from odoo.exceptions import UserError

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
    

class ReportTrialBalance(models.AbstractModel):
	_inherit = 'report.account.report_trialbalance'


	def account_layout_lines(self,account_lines=None,level=1):
		flag = True
		i = 1		
		while flag:
			flag = False
			grouped_lines = []
			#pdb.set_trace()
			
			
			#account_lines.sort(key=itemgetter("section"))
			account_lines.sort(key=lambda x: '999-' if x is None else x['section'])
			
			for key, valuesiter in groupby(account_lines, lambda item: item["section"]):
				group = {}
				group['section_name'] = key
				group['lines'] = list(v for v in valuesiter)
			
				group['ob'] = sum(line['ob'] for line in group['lines'])
				group['debit'] = sum(line['debit'] for line in group['lines'])
				group['credit'] = sum(line['credit'] for line in group['lines'])
				group['balance'] = sum(line['balance'] for line in group['lines'])

				section_id = group['lines'][0]['section_id']
				section = self.env['account.section'].browse(section_id)
					
				group['section_id'] = section.parent_id and section.parent_id.id or False
				group['section'] = section.parent_id and  (section.parent_id.code+'-'+section.parent_id.name) or False
				
				#group['section_id'] = section.parent_id and section.parent_id.id or section.id
				#group['section'] = section.parent_id and  (section.parent_id.code+'-'+section.parent_id.name) or (section.code+'-'+section.name)
				
				grouped_lines.append(group)
				if section.parent_id:
					flag = True
			
			if flag and i < level:
				i = i + 1
			else:
				flag = False
				
			account_lines = grouped_lines
				
		return account_lines

	def _get_accounts(self, accounts, display_account, level=1):
		""" compute the balance, debit and credit for the provided accounts
			:Arguments:
				`accounts`: list of accounts record,
				`display_account`: it's used to display either all accounts or those accounts which balance is > 0
			:Returns a list of dictionary of Accounts with following key and value
				`name`: Account name,
				`code`: Account code,
				`ob`: Opening Balance,
				`credit`: total amount of credit,
				`debit`: total amount of debit,
				`balance`: total amount of balance,
		"""

		account_result = {}
		account_ob_result = {}

		# Prepare sql query base on selected parameters from wizard
		tables, where_clause, where_params = self.env['account.move.line']._query_get()
		tables = tables.replace('"','')
		if not tables:
			tables = 'account_move_line'
		wheres = [""]
		if where_clause.strip():
			wheres.append(where_clause.strip())
		filters = " AND ".join(wheres)
				
		# compute the balance, debit and credit for the provided accounts
		request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
		params = (tuple(accounts.ids),) + tuple(where_params)
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
			account_result[row.pop('id')] = row

		filters = " AND ((account_move_line.date < %s) AND (account_move_line.date < %s))"
	
		request = ("SELECT account_id AS id, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
		#params = (tuple(accounts.ids),) + where_params[0]
		
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
			account_ob_result[row.pop('id')] = row

		account_res = []
		for account in accounts:
			res = dict((fn, 0.0) for fn in ['ob','credit', 'debit', 'balance'])
			currency = account.currency_id and account.currency_id or account.company_id.currency_id
			res['code'] = account.code
			res['name'] = account.name
			res['section_id'] = account.account_section.id
			res['section'] = account.account_section and (account.account_section.code+'-'+account.account_section.name) or ''
			if account.id in account_result.keys() or account.id in account_ob_result.keys():
				res['ob'] = account_ob_result.get(account.id,False) and account_ob_result[account.id].get('balance',0) or 0
				res['debit'] = account_result.get(account.id,False) and account_result[account.id].get('debit',0) or 0
				res['credit'] = account_result.get(account.id,False) and account_result[account.id].get('credit',0) or 0
				res['balance'] = (account_ob_result.get(account.id,False) and account_ob_result[account.id].get('balance',0) or 0) + (account_result.get(account.id,False) and account_result[account.id].get('balance',0) or 0)
			if display_account == 'all':
				account_res.append(res)
			if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
				account_res.append(res)
		
		if level == 0:
			return account_res
		else:
			account_res2 = self.account_layout_lines(account_res,level)		
			return account_res2


	@api.model
	def get_report_values(self, docids, data=None):
				
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))

		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids'))
		display_account = data['form'].get('display_account')
		accounts = docs if self.model == 'account.account' else self.env['account.account'].search([('company_id','=',self.env.user.company_id.id)],order='code')
		
		account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account,data['form'].get('level',1))
		
		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': account_res,
		}
		return docargs
	
	@api.multi
	def make_excel(self, data):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Trial Balance")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		SUM_STYLE = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		
		worksheet.write_merge(0, 1, 0, 5,"Trial Balance", style = style_title)
				
				
		display_account = data['form']['display_account']
		target_move = data['form']['target_move']
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']	
		
		if display_account == 'all':
			account_txt = 'All accounts'
		elif display_account == 'movement':
			account_txt = 'With movements'
		elif display_account == 'not_zero':
			account_txt = 'With balance not equal to zero'
		
		
		if target_move == 'all':
			target_txt = 'All Entries'
		if target_move == 'posted':
			target_txt = 'Posted Entries'
			
		worksheet.col(1).width = 367 * 40

		 
		worksheet.write_merge(3, 3, 0, 1, 'Display Account:', style=style_table_header)
		worksheet.write_merge(4, 4, 0, 1, account_txt, style=style_table_header)
		
		worksheet.write_merge(3, 3, 2, 2, 'Date From:', style=style_table_header)
		worksheet.write_merge(4, 4, 2, 2, date_from, style=style_table_header)
		
		worksheet.write_merge(3, 3, 3, 3, 'Date To:', style=style_table_header)
		worksheet.write_merge(4, 4, 3, 3, date_to, style=style_table_header)
		
		worksheet.write_merge(3, 3, 4, 5, 'Target Moves:', style=style_table_header)
		worksheet.write_merge(4, 4, 4, 5, target_txt, style=style_table_header)		
		
		
			
		row = 6
		col = 0   
		table_header = ['Code','Account','Opening', 'Debit','Credit','Balance']
		for i in range(6):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
				
		
		accounts = self.env['account.account'].search([('company_id','=',self.env.user.company_id.id)],order='code')
		account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account,0)
		
		row = 7
		for record in account_res:            
			row += 1
			col = 0  
			worksheet.write(row,col,record.get('code'))
			col +=1
			worksheet.write(row,col, "   " +record.get('name'))
			col +=1
			worksheet.write(row,col, record.get('ob'))
			col +=1
			worksheet.write(row,col, record.get('debit'))
			col +=1
			worksheet.write(row,col, record.get('credit'))
			col +=1
			worksheet.write(row,col, record.get('balance'))
		    
		for x in range(3):		
			formula = 'SUM(%s:%s)' % (
				xlwt.Utils.rowcol_to_cell(8, 3 + x),
				xlwt.Utils.rowcol_to_cell(row, 3 + x))
		
			worksheet.write(7, 3 + x, xlwt.Formula(formula), SUM_STYLE)
				
		file_data = io.BytesIO()		
		workbook.save(file_data)
				
		return file_data.getvalue()
		
        
        
		
