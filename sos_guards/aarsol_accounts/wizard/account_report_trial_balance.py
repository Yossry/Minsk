
from datetime import datetime
from odoo import fields, models, api, _
import StringIO
import base64
import csv
import re

from xlwt import *
import pdb

class AccountBalanceReport(models.TransientModel):
	_inherit = "account.balance.report"

	filedata = fields.Binary('File')
	filename = fields.Char('Filename', size = 64)
	
	def _get_accounts(self, accounts, display_account,date_from,date_to):
		
		account_result = {}
		account_ob_result = {}
				
		# compute the balance, debit and credit for the provided accounts
		request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM account_move_line WHERE account_id IN %s and date >= %s and date <= %s GROUP BY account_id")

		
		self.env.cr.execute(request, (tuple(accounts.ids),date_from,date_to))

		for row in self.env.cr.dictfetchall():
			account_result[row.pop('id')] = row
			
		request = ("SELECT account_id AS id, (SUM(debit) - SUM(credit)) AS balance" +\
			" FROM account_move_line WHERE account_id IN %s and date < %s and date < %s GROUP BY account_id")
		
		self.env.cr.execute(request, (tuple(accounts.ids),date_from,date_to))
		
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

				
		#account_res2 = self.account_layout_lines(account_res)		
		return account_res

	
	@api.multi
	def excell_export(self, data):
			
		
		display_account = self.display_account
		date_from = self.date_from
		date_to = self.date_to
		accounts = self.env['account.account'].search([('company_id','=',self.env.user.company_id.id)])
		account_res = self._get_accounts(accounts, display_account,date_from, date_to)
		
		fl = StringIO.StringIO()
		
		wb = Workbook()
		ws0 = wb.add_sheet('0')
		
		#data = self.read([])[0] 
		result = []
		result.append(['Code','Account','section','Opening','Debit','Credit','Balance'])
		
		
		for line in account_res:
			temp = []
			
			temp.append(line['code'])
			temp.append(line['name'])
			temp.append(line['section'])
			temp.append(line['ob'])
			temp.append(line['debit'])
			temp.append(line['credit'])
			temp.append(line['balance'])

			result.append(temp)
		
						
		for i,row in enumerate(result):
			for j,val in enumerate(row):
				ws0.write(i,j,val)
		
		file_name = 'trial_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.xls'
		wb.save(fl) 
		
		#fp = open(file_name)
		fl.seek(0)
		data = fl.read()
		#fp.close()
		out=base64.encodestring(data)
		self.write({'filedata' : out, 'filename':file_name})
		
		return {
			'name':'Trial Balance',
			'res_model':'account.common.report',
			'type':'ir.actions.act_window',
			'view_type':'form',
			'view_mode':'form',
			'target':'new',
			'nodestroy': True,			
			'res_id': self.id,
		} 
