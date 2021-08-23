import pdb
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from pytz import timezone
from odoo import api, models, _
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


class AARSOLReportGeneralLedger(models.AbstractModel):
	_name = "report.aarsol_accounts.aarsol_general_ledger_report"
	_description = "Customized General Ledger Report"

	def format_field_name(self, ordering, prefix='a', suffix='id'):
		"""Return an analytic field's name from its slot, prefix and suffix."""
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)

	def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
		"""
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """

		sos_flag = False
		cr = self.env.cr
		MoveLine = self.env['account.move.line']
		move_lines = {x: [] for x in accounts.ids}

		# Prepare initial sql query and Get the initial move lines
		if init_balance:
			init_tables, init_where_clause, init_where_params = MoveLine.with_context(
				date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
			init_wheres = [""]
			if init_where_clause.strip():
				init_wheres.append(init_where_clause.strip())
			init_filters = " AND ".join(init_wheres)
			filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
			sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
	               '' AS move_name, '' AS mmove_id, '' AS currency_code,\
	               NULL AS currency_id,\
	               '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
	               '' AS partner_name\
	               FROM account_move_line l\
	               LEFT JOIN account_move m ON (l.move_id=m.id)\
	               LEFT JOIN res_currency c ON (l.currency_id=c.id)\
	               LEFT JOIN res_partner p ON (l.partner_id=p.id)\
	               LEFT JOIN account_invoice i ON (m.id =i.move_id)\
	               JOIN account_journal j ON (l.journal_id=j.id)\
	               WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
			params = (tuple(accounts.ids),) + tuple(init_where_params)
			cr.execute(sql, params)
			for row in cr.dictfetchall():
				move_lines[row.pop('account_id')].append(row)

		sql_sort = 'l.date, l.move_id'
		if sortby == 'sort_journal_partner':
			sql_sort = 'j.code, p.name, l.move_id'

		if self.env.context['account_ids']:
			sos_flag = True
			ac_ids =self.env.context['account_ids']
			ac_recs = self.env['account.account'].search([('id','in',ac_ids)])
			tables, where_clause, where_params = MoveLine.with_context(account_ids=ac_recs)._query_get()
		if not sos_flag:
			tables, where_clause, where_params = MoveLine._query_get()

		# Prepare sql query base on selected parameters from wizard
		#tables, where_clause, where_params = MoveLine._query_get()
		wheres = [""]
		if where_clause.strip():
			wheres.append(where_clause.strip())
		filters = " AND ".join(wheres)
		filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

		# Get move lines base on sql query and Calculate the total balance of move lines
		sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
	           m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
	           FROM account_move_line l\
	           JOIN account_move m ON (l.move_id=m.id)\
	           LEFT JOIN res_currency c ON (l.currency_id=c.id)\
	           LEFT JOIN res_partner p ON (l.partner_id=p.id)\
	           JOIN account_journal j ON (l.journal_id=j.id)\
	           JOIN account_account acc ON (l.account_id = acc.id) \
	           WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
		params = (tuple(accounts.ids),) + tuple(where_params)
		cr.execute(sql, params)

		for row in cr.dictfetchall():
			balance = 0
			for line in move_lines.get(row['account_id']):
				balance += line['debit'] - line['credit']
			row['balance'] += balance
			move_lines[row.pop('account_id')].append(row)

		# Calculate the debit, credit and balance for Accounts
		account_res = []
		for account in accounts:
			currency = account.currency_id and account.currency_id or account.company_id.currency_id
			res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
			res['code'] = account.code
			res['name'] = account.name
			res['move_lines'] = move_lines[account.id]
			for line in res.get('move_lines'):
				res['debit'] += line['debit']
				res['credit'] += line['credit']
				res['balance'] = line['balance']
			if display_account == 'all':
				account_res.append(res)
			if display_account == 'movement' and res.get('move_lines'):
				account_res.append(res)
			if display_account == 'not_zero' and not currency.is_zero(res['balance']):
				account_res.append(res)

		return account_res

	def _get_account_move_entry_with_dimensions(self, accounts, init_balance, sortby, display_account,dimension_ids,dimension_group):
		cr = self.env.cr
		MoveLine = self.env['account.move.line']
		sos_flag = False

		dim_filters = ""
		dimH_filters = ""
		
		dims = {}		
		move_lines = {}
		
		if dimension_group:			
			structures = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',dimension_group[0])])
			grp_fld = self.format_field_name(structures.ordering,'l.a','id')
			dim_filters = " AND " + grp_fld + " is not null "
			
			sql = ("SELECT m.id FROM account_move_line l LEFT JOIN analytic_code m ON ("+grp_fld+"=m.id) WHERE l.account_id IN %s GROUP BY m.id")
			cr.execute(sql, (tuple(accounts.ids),))
				
			for code in self.env['analytic.code'].search([('nd_id','=',dimension_group[0])]):	
				if dims.get(dimension_group[0]):
					dims[dimension_group[0]].append(code.id)					
				else:
					dims[dimension_group[0]] = [code.id]					
						
			dimH_filters = dimension_group[1]				
			move_lines = dict(map(lambda x: (x, []), list(dims.values())[0]))
			
		else:   # Dimension Lines
			dim_rows = self.env['ledger.dimension.lines'].browse(dimension_ids)
			
			dimsH = {}
			for dim_row in dim_rows:
				if dims.get(dim_row.nd_id.id):
					dims[dim_row.nd_id.id].append(dim_row.code_id.id)
					dimsH[dim_row.nd_id.id].append(dim_row.code_id.name)
				else:
					dims[dim_row.nd_id.id] = [dim_row.code_id.id]
					dimsH[dim_row.nd_id.id] = [dim_row.code_id.name]
			
			conds = []	
			condsH = []

			for key,val in dims.items():
				structures = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',key)])
				fld = self.format_field_name(structures.ordering,'l.a','id')

				if len(val) == 1:
					conds.append(fld + ' = ' + str(val[0]))
				else:					
					conds.append(fld + ' in ' + str(tuple(val)))

			for key,val in dimsH.items():
				structures = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',key)])
				fld = structures.nd_id.name

				if len(val) == 1:
					condsH.append(fld + ' = ' + str(val[0]))
				else:					
					condsH.append(fld + ' in ' + str(tuple(val)))
		

			structures = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',list(dims.keys())[0])])
			grp_fld = self.format_field_name(structures.ordering,'l.a','id')
		
			dim_filters = " AND ".join(conds)
			dimH_filters = " AND ".join(condsH)	
			dim_filters = " AND "+ dim_filters
		
			move_lines = dict(map(lambda x: (x, []), list(dims.values())[0]))
		

		#for acc in accounts.ids:
		#	move_lines[acc] = move_dim_lines

		#move_lines = [(x,y) for x in accounts.ids for y in move_dim_lines]
		#move_lines = [list(zip(accounts.ids, p)) for p in permutations(move_dim_lines)]
		
		
		# Prepare initial sql query and Get the initial move lines
		if init_balance:
			init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
			init_wheres = [""]
			if init_where_clause.strip():
				init_wheres.append(init_where_clause.strip())
			init_filters = " AND ".join(init_wheres)
			filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
			sql = ("SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
				'' AS move_name, '' AS mmove_id, '' AS currency_code,\
				NULL AS currency_id,\
				'' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
				'' AS partner_name\
				FROM account_move_line l\
				LEFT JOIN account_move m ON (l.move_id=m.id)\
				LEFT JOIN res_currency c ON (l.currency_id=c.id)\
				LEFT JOIN res_partner p ON (l.partner_id=p.id)\
				LEFT JOIN account_invoice i ON (m.id =i.move_id)\
				JOIN account_journal j ON (l.journal_id=j.id)\
				WHERE l.account_id IN %s" + filters + ' GROUP BY l.account_id')
			params = (tuple(accounts.ids),) + tuple(init_where_params)
			cr.execute(sql, params)
			for row in cr.dictfetchall():
				move_lines[row.pop('account_id')].append(row)

		sql_sort = 'l.date, l.move_id'
		if sortby == 'sort_journal_partner':
			sql_sort = 'j.code, p.name, l.move_id'

		# Prepare sql query base on selected parameters from wizard
		#tables, where_clause, where_params = MoveLine._query_get()
		if self.env.context['account_ids']:
			sos_flag = True
			ac_ids =self.env.context['account_ids']
			ac_recs = self.env['account.account'].search([('id','in',ac_ids)])
			tables, where_clause, where_params = MoveLine.with_context(account_ids=ac_recs)._query_get()
		if not sos_flag:
			tables, where_clause, where_params = MoveLine._query_get()

		wheres = [""]
		if where_clause.strip():
			wheres.append(where_clause.strip())
		filters = " AND ".join(wheres)
		filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
		
		# Get move lines base on sql query and Calculate the total balance of move lines
		sql = ('SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname,\
			COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
			m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name, ' + grp_fld + ' AS grpfld\
			FROM account_move_line l\
			JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN res_currency c ON (l.currency_id=c.id)\
			LEFT JOIN res_partner p ON (l.partner_id=p.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			JOIN account_account acc ON (l.account_id = acc.id) \
			WHERE l.account_id IN %s' + dim_filters + filters + ' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, grpfld ORDER BY ' + sql_sort)
		params = (tuple(accounts.ids),) + tuple(where_params)
		cr.execute(sql, params)
		
		for row in cr.dictfetchall():
			balance = 0
			for line in move_lines.get(row['grpfld']):
				balance += line['debit'] - line['credit']
			row['balance'] += balance
			move_lines[row.pop('grpfld')].append(row)

		# Calculate the debit, credit and balance for Accounts
		account_res = []
		
		for dim_code in self.env['analytic.code'].browse(list(dims.values())[0]):
			res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
			res['code'] = dim_code.code or ''
			res['name'] = dim_code.name
			res['account_id'] = dim_code.id
			res['move_lines'] = move_lines[dim_code.id]
			for line in res.get('move_lines'):
				res['debit'] += line['debit']
				res['credit'] += line['credit']
				res['balance'] = line['balance']
			#if display_account == 'all':
			#	account_res.append(res)
			#if display_account == 'movement' and res.get('move_lines'):
			#	account_res.append(res)
			
			if res.get('move_lines'):
				account_res.append(res)
				
		return account_res,dimH_filters

	
	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))

		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

		init_balance = data['form'].get('initial_balance', True)
		sortby = data['form'].get('sortby', 'sort_date')
		display_account = data['form']['display_account']
		
		# ADDED THESE TWO LINES in aarsol_common function
		dimension_ids = data['form'].get('dimension_ids', False)
		dimension_group = data['form'].get('dimension_group', False)
		
		codes = []
		if data['form'].get('journal_ids', False):
			codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

		# these two if-else also added/modified
		if data['form'].get('account_ids', False):
			accounts = self.env['account.account'].browse(data['form'].get('account_ids'))
		else:
			accounts = self.env['account.account'].search([])

		
		if dimension_ids or dimension_group:
			accounts_res,dimH_filters = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry_with_dimensions(accounts, init_balance, sortby, display_account,dimension_ids,dimension_group)
		else:
			dimH_filters = "All"
			accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)	

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': accounts_res,
			'dimH_filters': dimH_filters,
			'print_journal': codes,
			'print_account': accounts,			
		}		
		return docargs
		
	
	
	#***** Excel Report *****#
	@api.multi
	def make_excel(self, data):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))

		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		
		init_balance = data['form'].get('initial_balance', True)
		sortby = data['form'].get('sortby', 'sort_date')
		display_account = data['form']['display_account']
		
		# ADDED THESE TWO LINES in aarsol_common function
		dimension_ids = data['form'].get('dimension_ids', False)
		dimension_group = data['form'].get('dimension_group', False)
		
		codes = []
		if data['form'].get('journal_ids', False):
			codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

		# these two if-else also added/modified
		if data['form'].get('account_ids', False):
			accounts = self.env['account.account'].browse(data['form'].get('account_ids'))
		else:
			accounts = self.env['account.account'].search([])

		if dimension_ids or dimension_group:
			accounts_res,dimH_filters = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry_with_dimensions(accounts, init_balance, sortby, display_account,dimension_ids,dimension_group)
		else:
			dimH_filters = "All"
			accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)	

		
		#***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("General Ledger")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header2 = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz right")
		
		worksheet.write_merge(0, 1, 0, 8,"General Ledger Report", style = style_table_header)
		row = 2
		col = 0
		
		#***** Table Heading *****#
		table_header = ['Date','JRNL','Partner','Ref','Move','Entry Label','Debit','Credit','Balance']
		for i in range(9):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
		i = 1
		#***** Table Data *****#
		for account in accounts_res:
			row += 1
			col = 0
			acc_name = ".. "+ account.get('code') +" "+ account.get('name')
			
			worksheet.write_merge(row,row,0,5,acc_name, style=style_table_header)
			col = 6
			worksheet.write(row,col, account.get('debit'), style=style_table_header)
			col +=1
			worksheet.write(row,col, account.get('credit'), style=style_table_header)
			col +=1
			worksheet.write(row,col, account.get('balance'), style=style_table_header)
			col +=1
				
			
			for line in  account['move_lines']:
				row += 1
				col = 0
				
				if line.get('balance') < 0:
					blan = format(abs(line.get('balance')),'.2f' or 0.00)
					bal = "("+ str(blan) + ")"
				else:
					bal = line.get('balance') 	  
			
				worksheet.write(row,col, line.get('ldate'))
				col +=1
				worksheet.write(row,col, line.get('lcode'))
				col +=1
				worksheet.write(row,col, line.get('partner_name'))
				col +=1
				worksheet.write(row,col, line.get('lref'))
				col +=1
				worksheet.write(row,col, line.get('move_name'))
				col +=1
				worksheet.write(row,col, line.get('lname'))
				col +=1
				worksheet.write(row,col,format(line.get('debit'),'.2f' or 0.00))
				col +=1
				worksheet.write(row,col, format(line.get('credit'),'.2f' or 0.00))
				col +=1
				
				worksheet.write(row,col, bal)
				col +=1
			
				i +=1
		
		file_data = io.BytesIO()		
		workbook.save(file_data)		
		return file_data.getvalue()	

