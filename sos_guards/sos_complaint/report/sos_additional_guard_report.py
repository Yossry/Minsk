import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _

class SosAdditionalGuardReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_additionalguard'
	_description = 'Additional Guards on Different Post Report'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		
		add_guard_obj = self.env['sos.additional.guard.proforma']	
		date_from = data['form']['date_from']		
		date_to = data['form']['date_to']
		
		project_dict = {}
		center_dict = {}
		
		project_total = 0
		p_permanent_total = 0
		p_deployment_total = 0
		p_temporary_total = 0
		p_withdraw_total = 0
		
		center_total = 0
		c_permanent_total = 0
		c_deployment_total = 0
		c_withdraw_total = 0
		c_temporary_total = 0
		
		self.env.cr.execute ("select p.name as name, \
			sum(case when ad.deployment_category='permanent' then ad.guards end) p_permanent, \
			sum(case when ad.deployment_category='temporary' then ad.guards end) p_temporary, \
			sum(case when ad.status='deployment' then ad.guards end) p_deployment, \
			sum(case when ad.status='withdraw' then ad.guards end) p_withdraw, \
			sum(ad.guards) as p_total from sos_additional_guard_proforma ad, sos_project p \
			where ad.dep_date >=%s and ad.dep_date <=%s and ad.project_id = p.id group by p.name", (date_from,date_to));
			
		project_dict = self.env.cr.dictfetchall()
		if project_dict:
			for p in project_dict:
				project_total = project_total + (p['p_total'] or 0)
				p_permanent_total = p_permanent_total + (p['p_permanent'] or 0)
				p_temporary_total = p_temporary_total + (p['p_temporary'] or 0)
				p_withdraw_total = p_withdraw_total + (p['p_withdraw'] or 0)
			
	
		self.env.cr.execute ("select c.name as name, \
				sum(case when ad.deployment_category='permanent' then ad.guards end) c_permanent, \
				sum(case when ad.deployment_category='temporary' then ad.guards end) c_temporary, \
				sum(case when ad.status='deployment' then ad.guards end) c_deployment, \
				sum(case when ad.status='withdraw' then ad.guards end) c_withdraw, \
				sum(ad.guards) as c_total from sos_additional_guard_proforma ad, sos_center c \
				where ad.dep_date >=%s and ad.dep_date <=%s and ad.center_id = c.id group by c.name", (date_from,date_to));
			
		center_dict = self.env.cr.dictfetchall()
		if center_dict:
			for c in center_dict:
				center_total = center_total + (c['c_total'] or 0)
				c_permanent_total = c_permanent_total + (c['c_permanent'] or 0)
				c_temporary_total = c_temporary_total + (c['c_temporary'] or 0)
				c_withdraw_total = c_withdraw_total + (c['c_withdraw'] or 0)
						
	#### Over All Report ###
		guard_ids = add_guard_obj.search([('dep_date','>=',date_from),('dep_date','<=',date_to)],order='dep_date,status' )		
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_additionalguard')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Project' : project_dict,
			'Center' : center_dict,
			
			'P_Permanent_Total' : p_permanent_total,
			'P_Temporary_Total' : p_temporary_total,
			'P_Withdraw_Total' : p_withdraw_total,
			'Project_Total' : project_total,
			
			'C_Permanent_Total' : c_permanent_total,
			'C_Temporary_Total' : c_temporary_total,
			'C_Withdraw_Total' : c_withdraw_total,
			'Center_Total' : center_total,
			
			
			'Guards' : guard_ids, 
			'get_date_formate' : self.get_date_formate,
		}
		
