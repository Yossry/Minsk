import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class SOSProjectGuardDetailReport(models.AbstractModel):
	_name = 'report.sos.report_projectguard_details'
	_description = 'SOS Project Guard Detail'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def get_total_project_center_branches(self,center_id, project_id):
		self.env.cr.execute("select count(*) from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s and project_id = %s",(center_id,project_id))
		posts = self.env.cr.dictfetchall()[0]		
		return posts['count']
		
	def get_total_project_center_guards(self, center_id,project_id):
		self.env.cr.execute("select sum(guards) qty from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s and project_id = %s",(center_id,project_id))
		guards = self.env.cr.dictfetchall()[0]		
		return guards['qty']		
	
	@api.model
	def _get_report_values(self, docids, data=None):
	
		center_obj = self.env['sos.center']
		center_ids = center_obj.search([])
		
		project_lines = []
		res = {}
		branches_grand_total =0
		guards_grand_total =0
		 
		project_ids = self.env['sos.project'].browse(data['form']['project_ids']) or False
		if project_ids:
			for project_id in project_ids:
				center_lines = []
				project_brances = 0
				project_guards = 0
					
				for center in center_ids:
					post_ids = self.env['sos.post'].search([('project_id', '=', project_id.id),('center_id', '=', center.id),('active', '=', True)])
					if post_ids:
						branch_total = self.get_total_project_center_branches(center.id,project_id.id) or 0
						total_guards =  self.get_total_project_center_guards(center.id,project_id.id) or 0
						
						project_brances += branch_total 
						project_guards += total_guards
						
						branches_grand_total += branch_total
						guards_grand_total += total_guards
						
						centers =({
							'name' : center.name,
							'branch_total' : branch_total,
							'total_guards' : total_guards,
							})
						center_lines.append(centers)	
							
				line=({
					'project' : project_id.name,
					'project_brances' :  project_brances,
					'project_guards' :  project_guards,
					'posts' : center_lines,
					})
				project_lines.append(line)	
		res = project_lines
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_projectguard_details')
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Centers' : res or False,
			'Branches' : branches_grand_total,
			'Guards'  : guards_grand_total,
			'get_date_formate' : self.get_date_formate,
		}
		
		
