import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _

class SOSCenterGuardPostWiseDetailReport(models.AbstractModel):
	_name = 'report.sos.report_center_postwiseguard_details'
	_description = 'SOS Center Post Wise Guard Details'
	
		
	@api.model
	def _get_report_values(self, docids, data=None):
		project_obj = self.env['sos.project']
		project_ids = project_obj.search([])
		
		center_lines = []
		res = {}
		guards_grand_total =0
		 
		center_ids = self.env['sos.center'].browse(data['form']['center_ids']) or False
		
		if center_ids:
			for center_id in center_ids:
				project_lines = []
				for project in project_ids:
					post_ids = self.env['sos.post'].search([('project_id', '=', project.id),('center_id', '=', center_id.id),('active', '=', True)])
					
					if post_ids:
						post_lines = []		
						for post_id in post_ids:
							self.env.cr.execute("select guards as qty from sos_post pp, res_partner p where p.post_id = pp.id and active = True  and pp.id = %s"%post_id.id)
							guards = self.env.cr.dictfetchall()[0]
							guards_grand_total += guards['qty']
							posts = ({
								'name' : post_id.name,
								'total' :guards['qty']
								})
							post_lines.append(posts)
							
						projects = ({
							'name' : project.name,
							'posts' : post_lines,
							})
						project_lines.append(projects)
				line=({
					'center' : center_id.name,
					'projects' : project_lines,
					})
				center_lines.append(line)	
			res = center_lines
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_center_postwiseguard_details')
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Centers' : res or False,
			'Guards_Total' : guards_grand_total or 0,
		}
		
		
