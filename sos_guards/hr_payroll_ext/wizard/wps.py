from datetime import datetime

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from io import StringIO
import base64
import csv

class hr_payslip_wps(models.TransientModel):

	_name = 'hr.payslip.wps'
	_description = 'WPS for Bank'

	filedata = fields.Binary('File')
	filename = fields.Char('Filename', size = 64, readonly=True)
	company_id = fields.Many2one('res.company')
	date = fields.Date('Date')	

	@api.multi
	def get_wps(self):
		slips_obj = self.env['hr.payslip']
		data = self.read([])[0]
		
		recs = slips_obj.search([('company_id','=',self.company_id.id),('date_from','<=',self.date),('date_to','>=',self.date)],order='code')   

		result = []
		result.append(['Employee #','Net Salary','Beneficiary Account','Beneficiary Name 1','Beneficiary Name 2','Beneficiary Name 3','Beneficiary Name 4',
			'Beneficiary Bank','Payment Description (Optional)','Basic Salary','Housing Allowance','Other Earnings','Deductions','Beneficiary ID'])

		i = 1
		for rec in recs:
			basic = 0
			hra = 0
			alw = 0
			net = 0
			deduction = 0

			for line in rec.line_ids:
				if line.salary_rule_id.category_id.code == 'NET':
					net += line.total
				if line.salary_rule_id.category_id.code == 'BASIC':
					basic += line.total
				if line.salary_rule_id.category_id.code == 'ALW':
					alw += line.total
				if line.salary_rule_id.category_id.code == 'DED':
					deduction += line.total
				if line.salary_rule_id.category_id.code == 'HR':
					hra += line.total	
			value = ''
			temp = []
			
			temp.append(str(i))
			temp.append(str(net))
			temp.append(str(rec.employee_id.bank_account_id.acc_number))
			temp.append(rec.employee_id.first_name)
			temp.append(rec.employee_id.second_name)
			temp.append(rec.employee_id.third_name)
			temp.append(rec.employee_id.fourth_name)
			temp.append(rec.employee_id.bank_account_id.bank_id.name)
			temp.append(str(rec.number))
			temp.append(str(basic))
			temp.append(str(hra))
			temp.append(str(alw))			
			temp.append(str(deduction))
			temp.append(str(rec.employee_id.iqama_number))

			result.append(temp)
			i = i + 1

		fp = StringIO.StringIO()
		writer = csv.writer(fp)
		for data in result:
			row = []
			for d in data:
				if isinstance(d, basestring):
					d = d.replace('\n',' ').replace('\t',' ')
					try:
						d = d.encode('utf-8')
					except:
						pass
				if d is False: d = None
				row.append(d)
			writer.writerow(row)

		fp.seek(0)
		data = fp.read()
		fp.close()
		out=base64.encodestring(data)
		file_name = 'midchem_' + str(self.date)+'_wps.csv' 

		self.write({'filedata':out, 'filename':file_name})
        
		return {
			'name':'WPS File',
			'res_model':'hr.payslip.wps',
			'type':'ir.actions.act_window',
			'view_type':'form',
			'view_mode':'form',
			'target':'new',
			'nodestroy': True,			
			'res_id': self.id,
		} 
