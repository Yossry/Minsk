import pdb
from datetime import datetime
from odoo import tools
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SOSCenter(models.Model):
	_name = "sos.center"
	_inherit = ['mail.thread']
	_description = "SOS Center"
	_rec_name = "code"
	_order = 'name'
	
	name =  fields.Char('Center Name', size=64)
	code =  fields.Char('Center Code', size=16)
	region_id = fields.Many2one('sos.region','Region')
	regional_head_id = fields.Many2one('hr.employee','Regional Head')
	supervisor_id = fields.Many2one('hr.employee','Supervisor')
	attendance_min_date = fields.Date('Min. Attendance Date',write=['sos.group_superusers'])
	attendance_max_date = fields.Date('Max. Attendance Date',write=['sos.group_superusers'])
	post_ids = fields.One2many('sos.post', 'center_id' , string = 'Posts', help = 'Posts related to this Center')
	user_ids = fields.Many2many('res.users', 'center_user_rel', 'center_id', 'user_id', 'Users')
	city_ids = fields.One2many('sos.city', 'center_id' , string = 'Cities', help = 'Cities related to this Center')
	
	
	## For Center Salary Rates Report ##
	def get_center_projects(self, center_id):
		project_obj = self.env['sos.project']
		project_ids = project_obj.search([])
		final_projects = []
		
		for project in project_ids:
			post_ids = self.env['sos.post'].search([('project_id', '=', project.id),('center_id', '=', center_id),('active', '=', True)])
			if post_ids:
				final_projects.append(project)
		return final_projects
	
	## For Center Salary Rates Report ##
	def get_center_project_posts(self, center_id, project_id):
		post_obj = self.env['sos.post']
		post_ids = post_obj.search([('center_id', '=', center_id),('project_id', '=', project_id),('active', '=', True)])	
		return post_ids
	
	## For Center Invoice Rate Report ##	
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

	#Cron Job For Attendance Date Setting
	@api.model
	def auto_date_setting(self, nlimit=100):
		today_date = str(datetime.now())[:10]
		posts = False

		centers = self.env['sos.center'].search([])
		projects = self.env['sos.project'].search([])
		posts = self.env['sos.post'].search([('center_id', 'in', centers.ids),('active','=',True)])
		
		date_1 = datetime.strptime(today_date, "%Y-%m-%d")
		#min_date = (date_1 + relativedelta.relativedelta(days=-1))
		
		#Centers
		for center in centers:
			center.attendance_min_date = today_date
			center.attendance_max_date = today_date
		
		#Projects
		for project in projects:
			project.attendance_min_date = today_date
			project.attendance_max_date = today_date	
		
		#Posts
		for post in posts:
			post.attendance_min_date = today_date
			post.attendance_max_date = today_date
	


class SOSRegion(models.Model):
	_name = "sos.region"
	_description = "SOS Region"
	_rec_name = "code"
	_order = 'name'

	name =  fields.Char('Region Name', size=64)
	code =  fields.Char('Region Code', size=16)
	center_ids = fields.One2many('sos.center', 'region_id' , string = 'Center', help = 'Centers related to this Region')
	user_ids = fields.Many2many('res.users', 'region_user_rel', 'region_id', 'user_id', 'Users')
				
	
