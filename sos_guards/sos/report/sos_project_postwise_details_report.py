import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _

class SOSProjectGuardPostWiseDetailReport(models.AbstractModel):
	_name = 'report.sos.report_project_postwiseguard_details'
	_description = 'SOS Project Post Wise Guard Details Report'
	
	@api.model
	def _get_report_values(self, docids, data=None):
		center_obj = self.env['sos.center']
		center_ids = center_obj.search([])
		project_lines = []
		res = {}
		guards_grand_total =0
		 
		project_ids = self.env['sos.project'].browse(data['form']['project_ids']) or False
		
		if project_ids:
			for project_id in project_ids:
				center_lines = []
				for center in center_ids:
					post_ids = self.env['sos.post'].search([('project_id', '=', project_id.id),('center_id', '=', center.id),('active', '=', True)])
					
					if post_ids:
						post_lines = []		
						for post_id in post_ids:
							self.env.cr.execute("select guards as qty from sos_post pp, res_partner p where p.post_id = pp.id and active = True and pp.id= %s"%post_id.id)
							guards = self.env.cr.dictfetchall()[0]
							guards_grand_total += guards['qty']
							posts = ({
								'name' : post_id.name,
								'total' :guards['qty']
								})
							post_lines.append(posts)
							
						centers = ({
							'name' : center.name,
							'posts' : post_lines,
							})
						center_lines.append(centers)
				line=({
					'project' : project_id.name,
					'centers' : center_lines,
					})
				project_lines.append(line)	
			res = project_lines
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_project_postwiseguard_details')
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Projects' : res or False,
			'Guards_Total' : guards_grand_total or 0,
		}
