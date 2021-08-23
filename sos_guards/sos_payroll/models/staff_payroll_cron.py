import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import api, fields, models
from odoo import tools
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.tools.safe_eval import safe_eval as eval
DATETIME_FORMAT = "%Y-%m-%d"


class staff_payslip_cron(models.Model):
	_name = 'staff.payslip.cron'
	_description = 'Payslip Cron Jobs'
	_order = 'id desc'
		
	employee_id = fields.Many2one('hr.employee','Employee')
	center_id = fields.Many2one('sos.center','Center')
	department_id = fields.Many2one('hr.department','Department')	
	date_from = fields.Date("Date From")
	date_to = fields.Date("Date To")
	state = fields.Selection([('draft', 'Draft'),('generate', 'Generate'),('done', 'Done')], 'Status', readonly=True,default='draft')
	slip_id = fields.Many2one('hr.payslip','Payslip')
	
	@api.one
	def generate_slips(self, nlimit=100):
		emp_pool = self.env['hr.employee']
		contract_obj = self.env['hr.contract']
		slip_pool = self.env['hr.payslip']
		slip_ids = self.env['hr.payslip']
		cron_draft_slips = self.search([('state','=','draft')],limit=nlimit)
		
		if cron_draft_slips:
			for cron_slip in cron_draft_slips:
				ttyme = datetime.fromtimestamp(time.mktime(time.strptime(cron_slip.date_from, "%Y-%m-%d")))
				contract_id = contract_obj.search([('employee_id','=',cron_slip.employee_id.id),('state','=','open')])
				
				worked_days_line_ids = slip_pool.get_worked_day_lines_monthly_attendance(contract_id.id, cron_slip.date_from, cron_slip.date_to)
				worked_days_lines = slip_pool.worked_days_line_ids.browse([])
				
				for r in worked_days_line_ids:
					worked_days_lines += worked_days_lines.new(r)
					
				input_line_ids = slip_pool.get_inputs(contract_id.id, cron_slip.date_from, cron_slip.date_to)
				input_lines = slip_pool.input_line_ids.browse([])
				for r in input_line_ids:
					input_lines += input_lines.new(r)	 
				
				res = {
					'employee_id': cron_slip.employee_id.id,
					'name':  _('Salary Slip of %s for %s') % (cron_slip.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
					'struct_id': contract_id.struct_id.id or False,
					'contract_id': contract_id.id or False,
					'input_line_ids': [(0, 0, x) for x in input_lines],
					'worked_days_line_ids': [(0, 0, x) for x in worked_days_lines],
					'date_from': cron_slip.date_from,
					'date_to': cron_slip.date_to,
					'journal_id': contract_id.journal_id.id,
				}
				slip_id = slip_pool.create(res)
				cron_slip.write({'state':'generate','slip_id':slip_id.id})
				
				slip_ids += slip_id
			slip_ids.compute_sheet()
