import time
from datetime import datetime
from dateutil import relativedelta
import pdb
from odoo import api, fields, models

class guards_payslips_cron_wizard(models.TransientModel):
	_name ='guards.payslips.cron.wizard'
	_description = 'Generate Cron Entries'

	paidon = fields.Boolean('Paidon',default=False)
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	project_ids = fields.Many2many('sos.project', 'payslip_cron_project_rel',string='Filter on Projects', help="Only selected Projects Salaries will be generated.")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="Only selected Centers Salaries will be generated.")
	employee_ids = fields.Many2many('hr.employee', string='Filter on Employees', help="Only selected Employees Salaries will be generated.")
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="Only selected Employees Salaries will be generated.")
	exclude_project_ids = fields.Many2many('sos.project', 'payslip_cron_exclude_project_rel',string='Exclude Projects', help="Selected Projects Salaries will not be generated.",
		default=lambda self: self.env['sos.project'].search([('id','in',[30])]))
		

	@api.multi
	def generate_post_cron_entry(self):
		cron_post_pool = self.env['posts.payslip.cron']
		post_pool = self.env['sos.post']

		for data in self:		
			
			post_domain = []	
			if data.center_ids:
				post_domain.append(('center_id','in', data.center_ids.ids))
			if data.project_ids:
				post_domain.append(('project_id','in', data.project_ids.ids))
			if data.post_ids:
				post_domain.append(('id','in', data.post_ids))	
			
			post_domain.append(('active','=', True))
			
			post_ids = post_pool.search(post_domain)
			for post in post_ids:
				res = {
					'post_id': post.id,
					'date_from': data.date_from,
					'date_to': data.date_to,
					'state': 'draft',
					'center_id': post.center_id.id,
					'project_id': post.project_id.id,
				}								
				cron_rec = cron_post_pool.sudo().create(res)
					
			
		return {'type': 'ir.actions.act_window_close'}

	@api.multi
	def reaudit(self):
		cron_slip_pool = self.env['guards.payslip.cron']
		
		for data in self:
			rec_domain = [('date_from','>=',data.date_from),('date_to','<=',data.date_to),('state','=','difference')]
			rec_ids = cron_slip_pool.search(rec_domain)
			if rec_ids:
				rec_ids.write({'state':'generate'})	

	@api.multi
	def generate_cron_entry(self):
		cron_slip_pool = self.env['guards.payslip.cron']
		emp_pool = self.env['hr.employee']
		att_pool = self.env['sos.guard.attendance']

		for data in self:		
			
			emp_domain = []	
			if data.center_ids:
				emp_domain.append(('center_id','in', data.center_ids.ids))
			if data.project_ids:
				emp_domain.append(('project_id','in', data.project_ids.ids))
			
			emp_domain.append('|')
			emp_domain.append(('resigdate','=', False))
			emp_domain.append(('resigdate','>=', data.date_from))
			
			emp_ids = emp_pool.search(emp_domain)
			for emp in emp_ids:
				
				att_domain = [('name','>=',data.date_from),('name','<=',data.date_to),('slip_id','=',False),('employee_id','=',emp.id),('paidon','=',data.paidon)]
				if data.exclude_project_ids:
					att_domain.append(('project_id','not in',data.exclude_project_ids.ids))
				att_ids = att_pool.search(att_domain)
				if att_ids:
					att_ids.write({'state':'counted'})

					res = {
						'employee_id': emp.id,
						'date_from': data.date_from,
						'date_to': data.date_to,
						'paidon': data.paidon,
						'state': 'draft',
						'center_id': emp.center_id.id,
						'project_id': emp.project_id and emp.project_id.id or False,
						'exclude_project_ids': [(6, 0, data.exclude_project_ids.ids)]
					}								
					cron_rec = cron_slip_pool.sudo().create(res)
					
			
		return {'type': 'ir.actions.act_window_close'}
