import time
import pdb
from odoo import api, fields, models

class SOSGuardsAttendanceDates(models.TransientModel):
	_name = "guards.attendance.dates.setting"
	_description = "Attendance Date Setting"
	
	attendance_min_date = fields.Date('Min. Attendance Date')
	attendance_max_date = fields.Date('Max. Attendance Date')
	criteria = fields.Selection( [('center','Centers'),('project','Projects'),('post','Posts')], "Criteria", default='center')
	post_ids = fields.Many2many('sos.post', string='Filter on Posts', help="""Only selected Posts will be printed. Leave empty to print all Posts.""")                           		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          
	
	
	@api.multi
	def set_dates(self):
		post_obj = self.env['sos.post']
		domain =[]
		projects = []
		centers = []
		
		for data in self:
			attendance_min_date = data.attendance_min_date
			attendance_max_date = data.attendance_max_date
			
			post_ids  = data.post_ids or False
			if post_ids:
				post_ids = post_obj.search([('id', 'in', post_ids.ids)])
				for post_id in post_ids:
					post_id.attendance_min_date = attendance_min_date
					post_id.attendance_max_date = attendance_max_date
		
			if not post_ids:
				center_ids = data.center_ids or False
				if center_ids:
					for c in center_ids:
						c.attendance_min_date = attendance_min_date
						c.attendance_max_date = attendance_max_date	
						
					domain = [('center_id', 'in', center_ids.ids),('active','=',True)]
					posts_id = post_obj.search(domain)
					post_ids = posts_id
					
					self.env.cr.execute("select distinct project_id from sos_post where id in %s" % str(tuple(post_ids.ids,)))
					project_dict = self.env.cr.dictfetchall()
					
					for p in project_dict:
						projects.append(p['project_id'])
					
					self.env.cr.execute("update sos_project set attendance_min_date=%s, attendance_max_date=%s where id in %s", (attendance_min_date,attendance_max_date,tuple(projects)))
					for post_id in post_ids:
						post_id.attendance_min_date = attendance_min_date
						post_id.attendance_max_date = attendance_max_date
			
			if not post_ids:
				project_ids= data.project_ids
				if project_ids:
					for p in project_ids:
						p.attendance_min_date = attendance_min_date
						p.attendance_max_date = attendance_max_date
						
					domain = [('project_id', 'in', project_ids.ids),('active','=',True)]
					posts_id = post_obj.search(domain)
					post_ids = posts_id
					
					self.env.cr.execute("select distinct center_id from sos_post where id in %s" % str(tuple(post_ids.ids,)))
					center_dict = self.env.cr.dictfetchall()
					
					for c in center_dict:
						centers.append(c['center_id'])
					self.env.cr.execute("update sos_center set attendance_min_date=%s, attendance_max_date=%s where id in %s", (attendance_min_date,attendance_max_date,tuple(centers)))	
						
					for post_id in post_ids:
						post_id.attendance_min_date = attendance_min_date
						post_id.attendance_max_date = attendance_max_date	
		
		return True
