import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import models, fields, api, _

class employee_contract_wizard(models.TransientModel):
	_name = 'employee.contract.wizard'
	_description = 'Employee Contract Wizard'
	
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id.id)
	segment_id = fields.Many2one('hr.segmentation', string='Segment')
	sub_segment_id = fields.Many2one('hr.sub.segmentation', string='Sub Segment')
	employee_status = fields.Selection([('Active','Active'),('All','All')], default='Active')
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('hr_ext.report_employee_contract').with_context(landscape=True).report_action(self, data=datas)
