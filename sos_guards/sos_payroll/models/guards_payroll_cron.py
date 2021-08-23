from calendar import isleap
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

import logging
_logger = logging.getLogger(__name__)


DATETIME_FORMAT = "%Y-%m-%d"

class posts_payslip_cron(models.Model):
	_name = 'posts.payslip.cron'
	_description = 'Posts Payslip Cron Jobs'
	_order = 'id desc'
		
	post_id = fields.Many2one('sos.post','Post')
	center_id = fields.Many2one('sos.center','Center')
	project_id = fields.Many2one('sos.project','Project')	
	date_from = fields.Date("Date From")
	date_to = fields.Date("Date To")
	state = fields.Selection([('draft', 'Draft'),('generate', 'Generate'),('to_audit', 'Audit'),('difference', 'Difference'),('done', 'Done'),('noc','No Contract'),('error','Error')], 'Status', readonly=True,default='draft')
	note = fields.Text('Note')
	audit_result = fields.Selection([('valid','Valid'),('manual','Manual'),('less','Less'),('more','More')],'Audit Result')

	@api.model		
	def audit_posts(self, nlimit=100):
		invoice_pool = self.env['account.invoice']
		work_pool = self.env['guards.payslip.worked_days']
		
		cron_audit_posts = self.search([('state','=','draft')],limit=nlimit)			
		for cron_post in cron_audit_posts:	
			flag = True
			
			post_work_ids = work_pool.search([('post_id','=',cron_post.post_id.id),('payslip_id.date_from','=',cron_post.date_from)])	
			duty_days = sum(line.number_of_days for line in post_work_ids)
				
			invoice_ids = invoice_pool.search([('post_id','=',cron_post.post_id.id),('date_invoice','>=',cron_post.date_from),('date_invoice','<=',cron_post.date_to)])	
			invoice_days = 0
			for invoice_id in invoice_ids:
				invoice_days += sum(line.quantity for line in invoice_id.invoice_line_ids)

			if duty_days != invoice_days:
				flag = False
				cron_post.note = "Duty = " + str(duty_days) + ",Invoice (" + str(len(invoice_ids)) + ") = " + str(invoice_days)
				cron_post.audit_result = 'less' if duty_days < invoice_days else 'more'
				cron_post.write({'state':'difference'})
				
			if flag:
				cron_post.audit_result = 'valid'
				cron_post.write({'state':'done'})

class guards_payslip_cron(models.Model):
	_name = 'guards.payslip.cron'
	_description = 'Payslip Cron Jobs'
	_order = 'id desc'
		
	employee_id = fields.Many2one('hr.employee','Guard')
	center_id = fields.Many2one('sos.center','Center')
	project_id = fields.Many2one('sos.project','Project')	
	date_from = fields.Date("Date From")
	date_to = fields.Date("Date To")
	state = fields.Selection([('draft', 'Draft'),('generate', 'Generate'),('to_audit', 'Audit'),('difference', 'Difference'),('done', 'Done'),('noc','No Contract'),('error','Error')], 'Status', readonly=True,default='draft')
	slip_id = fields.Many2one('guards.payslip','Payslip')
	paidon = fields.Boolean('Paidon')
	exclude_project_ids = fields.Many2many('sos.project', 'payslip_exclude_project_rel','cron_id','project_id',string='Exclude Projects')
	note = fields.Text('Note',related='slip_id.note')
	audit_result = fields.Selection('Audit Status',related='slip_id.audit_result',store=True)

	@api.model		
	def generate_slips(self, nlimit=100):
		emp_pool = self.env['hr.employee']
		invoice_pool = self.env['account.invoice']
		work_pool = self.env['guards.payslip.worked_days']
		slip_pool = self.env['guards.payslip']
		slip_ids = self.env['guards.payslip']
		audit_pool = self.env['guards.payslip.audit']

		cron_draft_slips = self.search([('state','=','draft')],limit=nlimit)		
		if cron_draft_slips:
			for cron_slip in cron_draft_slips:
				_logger.info('.... cron called is called for slip generation .. %r..............', cron_slip.id)				
				slip_data = slip_pool.on_change_employee_id(cron_slip.date_from, cron_slip.date_to, cron_slip.employee_id.id, cron_slip.paidon, 
					exclude_project_ids=cron_slip.exclude_project_ids, contract_id=False)
				
				invoice_id = False			
				if cron_slip.paidon:					
					invoice_ids = invoice_pool.search([('post_id','=',slip_data['value'].get('worked_days_line_ids')[0]['post_id']),('date_invoice','>=',cron_slip.date_from),('date_invoice','<=',cron_slip.date_to)])
					invoice_id = invoice_ids and invoice_ids[0].id or False
				
				if slip_data['value'].get('contract_id', False):
					res = {
						'employee_id': cron_slip.employee_id.id,
						'name': slip_data['value'].get('name', False),
						'struct_id': slip_data['value'].get('struct_id', False),
						'contract_id': slip_data['value'].get('contract_id', False),
						#'payslip_run_id': context.get('active_id', False),
						'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
						'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
						#'attendance_line_ids': [(4, x, False) for x in slip_data['value'].get('attendance_line_ids', False)],
						#'attendance_line_ids': [(0, 0, x) for x in slip_data['value'].get('attendance_line_ids', False)],				
						#'attendance_line_ids': slip_data['value'].get('attendance_line_ids', False),				
						'date_from': cron_slip.date_from,
						'date_to': cron_slip.date_to,
						'credit_note': False,
						'journal_id': 24, #slip_pool._get_default_journal().id,
						'accowner': slip_data['value'].get('accowner', False),
						'bank': slip_data['value'].get('bank', False),
						'bankacc': slip_data['value'].get('bankacc', False),
						'bankacctitle': slip_data['value'].get('bankacctitle', False),
						'center_id': slip_data['value'].get('center_id', False),
						'company_id': slip_data['value'].get('company_id', False),
						'paidon': slip_data['value'].get('paidon', False),
						'post_id': slip_data['value'].get('post_id', False),
						'project_id': slip_data['value'].get('project_id', False),
						'invoice_id': invoice_id,
						'abl_incentive': slip_data['value'].get('abl_incentive', False),
						'abl_incentive_amt': slip_data['value'].get('abl_incentive_amt', False),
						'paid_leaves': slip_data['value'].get('paid_leaves', 0),
						'bank_temp_id': False,
					}			
					slip_id = slip_pool.create(res)
					_logger.info('.... slip is generated .. %r..............', slip_id.id)	
					cron_slip.write({'state':'generate','slip_id':slip_id.id})
									

					att_ids = self.env['sos.guard.attendance'].search([('name', '>=', cron_slip.date_from), ('name', '<=', cron_slip.date_to), ('employee_id', '=', cron_slip.employee_id.id),
						('project_id', 'not in', cron_slip.exclude_project_ids.ids),('slip_id','=',False)])
		
					att_ids.write({'slip_id':slip_id.id})
					slip_id.compute_sheet()
					#slip_ids += slip_id
				else:
					cron_slip.write({'state':'noc'})	
			#slip_ids.compute_sheet()

		else:		
			#pdb.set_trace()
			cron_generate_slips = self.search([('state','=','generate')],limit=nlimit)			
			for cron_slip in cron_generate_slips:
				_logger.info('.... cron is called for slip audited .. %r..............', cron_slip.id)					
				flag = True
				post_audit_ids = False
				if cron_slip.slip_id:
					if cron_slip.slip_id.move_id:
						cron_slip.slip_id.audit_result = 'manual'
						cron_slip.write({'state':'done'})		
						flag = False					
					else:			
						work_ids = cron_slip.slip_id.worked_days_line_ids
						cron_slip.slip_id.note = False
						for work_id in work_ids:
							post_work_ids = work_pool.search([('post_id','=',work_id.post_id.id),('payslip_id.date_from','=',cron_slip.date_from)])	
							duty_days = sum(line.number_of_days for line in post_work_ids)
					
							post_audit_ids = audit_pool.search([('post_id','=',work_id.post_id.id),('state','in',['draft','process'])])	
							if post_audit_ids:
								#post_audit_ids_list = post_audit_ids_list + post_audit_ids
								diff_days = sum(line.diff for line in post_audit_ids) 
								duty_days += diff_days

							invoice_ids = invoice_pool.search([('post_id','=',work_id.post_id.id),('date_invoice','>=',cron_slip.date_from),('date_invoice','<=',cron_slip.date_to)])	
							invoice_days = 0
							for invoice_id in invoice_ids:
								### to skip one day added in the ABL Payslips ###
								if invoice_id.incentive == False:
									if invoice_id.type == 'out_refund':
										invoice_days -= sum(line.quantity for line in invoice_id.invoice_line_ids)
									else:
										invoice_days += sum(line.quantity for line in invoice_id.invoice_line_ids)

							if duty_days != invoice_days:
								flag = False
								if cron_slip.slip_id.note:
									cron_slip.slip_id.note = cron_slip.slip_id.note + "\n" + work_id.post_id.name + ":: Duty = " + str(duty_days) + ",Invoice = " + str(invoice_days)
								else:
									cron_slip.slip_id.note = work_id.post_id.name + ":: Duty = " + str(duty_days) + ",Invoice = " + str(invoice_days)
								cron_slip.slip_id.audit_result = 'less' if duty_days < invoice_days else 'more'
								cron_slip.write({'state':'difference'})
								if post_audit_ids:
									post_audit_ids.write({'state':'error'})
				else:
					cron_slip.write({'state':'error'})
					flag = False	
				if flag:
					cron_slip.slip_id.guards_process_sheet()
					cron_slip.slip_id.audit_result = 'valid'
					if post_audit_ids:
						post_audit_ids.write({'state':'process'})
					cron_slip.write({'state':'done'})

						
	@api.model		
	def audit_slips(self, nlimit=100):
		emp_pool = self.env['hr.employee']
		invoice_pool = self.env['account.invoice']
		work_pool = self.env['guards.payslip.worked_days']
		slip_pool = self.env['guards.payslip']
		slip_ids = self.env['guards.payslip']
		audit_pool = self.env['guards.payslip.audit']

		cron_audit_slips = self.search([('state','=','to_audit')],limit=nlimit)			
		for cron_slip in cron_audit_slips:	
			flag = True
			post_audit_ids = False
			if cron_slip.slip_id:
				work_ids = cron_slip.slip_id.worked_days_line_ids
				cron_slip.slip_id.note = False
				for work_id in work_ids:
					post_work_ids = work_pool.search([('post_id','=',work_id.post_id.id),('payslip_id.date_from','=',cron_slip.date_from)])	
					duty_days = sum(line.number_of_days for line in post_work_ids)
				
				
					invoice_ids = invoice_pool.search([('post_id','=',work_id.post_id.id),('date_invoice','>=',cron_slip.date_from),('date_invoice','<=',cron_slip.date_to)])	
					invoice_days = 0
					for invoice_id in invoice_ids:
						invoice_days += sum(line.quantity for line in invoice_id.invoice_line_ids)

					if duty_days != invoice_days:
						flag = False
						if cron_slip.slip_id.note:
							cron_slip.slip_id.note = cron_slip.slip_id.note + "\n" + work_id.post_id.name + ":: Duty = " + str(duty_days) + ",Invoice (" + str(len(invoice_ids)) + ") = " + str(invoice_days)
						else:
							cron_slip.slip_id.note = work_id.post_id.name + ":: Duty = " + str(duty_days) + ",Invoice (" + str(len(invoice_ids)) + ") = " + str(invoice_days)
						cron_slip.slip_id.audit_result = 'less' if duty_days < invoice_days else 'more'
						cron_slip.write({'state':'difference'})
				
				if flag:
					cron_slip.slip_id.audit_result = 'valid'
					cron_slip.write({'state':'done'})







