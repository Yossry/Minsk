import pdb
from datetime import datetime
from odoo import tools
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SOSProject(models.Model):
	_name = "sos.project"
	_description = "SOS Projects"
	_order = 'name'

	@api.one	
	def _compute_guard(self):
		result = []		
		employee_ids = self.env['hr.employee'].search([('project_id', '=', self.id)])
		for employee in employee_ids:
			result.append(employee.id)
		return result
	
	@api.multi
	def _calc_emp_point(self):
		''' This function will automatically calculates the points of particular employee.'''
		for project in self:
			emp_ids = self.env['hr.employee'].search([('project_id', '=', project.id),('current','=',True)])
			points=0
			count=0
			for emp in emp_ids:
				points = points + emp.points
				count = count + 1
			if count == 0:
				count = 1
			project.emp_points = points / count
	
	@api.one
	def _project_aged_balance(self):		
		Invoice = self.env['account.invoice']
		start_date = datetime.strptime('2016-07-01', "%Y-%m-%d").date()
		today = datetime.today().strftime('%Y-%m-%d')
		invoices = Invoice.search([('post_id', 'in', self.post_ids.ids),('type', '=', 'out_invoice'),('date_due', '>=', start_date),('date_due','<=', today),('residual', '>', 0)])
		total = 0
		
		for invoice in invoices:
			total = total + invoice.residual
		self.aged_balance = total	

	name = fields.Char('Project Name', size=256)
	accountno = fields.Char('Account', size=64) 
	active = fields.Boolean('Active')
	project_coordinator_id = fields.Many2one('hr.employee','Project Coordinator',domain=[('is_guard','=',False)])
	emp_points = fields.Integer(compute='_calc_emp_point', store=True, string='Points', readonly=True)
	aged_balance = fields.Float('Aged Balance',compute='_project_aged_balance')
	centralized = fields.Boolean("Centralized")
	attendance_min_date = fields.Date('Min. Attendance Date',write=['sos.group_superusers'])
	attendance_max_date = fields.Date('Max. Attendance Date',write=['sos.group_superusers'])
	
	post_ids = fields.One2many('sos.post', 'project_id', string = 'Posts', help = 'Posts related to this Project')
	coordinator_ids = fields.Many2many('res.users', 'sos_project_user_rel', 'project_id', 'user_id', 'Coordinators')
	employee_ids = fields.One2many('hr.employee','project_id', domain=[('current', '=', True)], string='Project Guards')
	start_date = fields.Date('Project Start Date') 
	
	## For Salary Rate Report ##
	def get_project_centers(self, project_id):
		center_obj = self.env['sos.center']
		center_ids = center_obj.search([])
		final_centers = []
		for center in center_ids:
			post_ids = self.env['sos.post'].search([('project_id', '=', project_id),('center_id', '=', center.id),('active', '=', True)])
			if post_ids:
				final_centers.append(center)
		return final_centers

	## For Salary Rate Report ##	
	def get_center_project_posts(self, center_id, project_id):
		post_obj = self.env['sos.post']
		post_ids = post_obj.search([('center_id', '=', center_id),('project_id', '=', project_id),('active', '=', True)])
		return post_ids
	
	## For Invoice Rate Report ##	
	def get_post_jobs(self, post_id):
		jobs_obj = self.env['sos.post.jobs']
		jobs_ids = jobs_obj.search([('post_id', '=', post_id)])
		
		res = []
		civil = ''
		armed = ''
		supervisor = ''
		for job in jobs_ids:
			if job.contract_id.name == 'Civil':
				civil = ' ' + str(job.guards) + ' * ' + str(job.rate)
			if job.contract_id.name == 'Armed':
				armed = ' ' + str(job.guards) + ' * ' + str(job.rate)
			if job.contract_id.name == 'Supervisor':
				supervisor = ' ' + str(job.guards) + ' * ' + str(job.rate)
			
		res.append({
			'civil' : civil,
			'armed' : armed,
			'supervisor' : supervisor,
		})
		return res