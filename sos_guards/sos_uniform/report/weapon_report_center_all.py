import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ReportWeaponCenterAll(models.AbstractModel):
	_name = 'report.sos_uniform.report_weaponcenterall'
	_description = 'All Centers Weapon Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		centers = self.env['sos.center'].search([], order='name')
		res = []
		
		total_bore_32 = 0
		total_bore_30 = 0
		total_bore_12 = 0
		total_bore_222 = 0 
		total_bore_44 = 0 
		total_mm_7 = 0
		total_mm_8 = 0
		total_mm_9 = 0
		total_mp_5 = 0
		total_shilling = 0
		
		total_bore_32_rounds = 0
		total_bore_30_rounds = 0
		total_bore_12_rounds = 0
		total_bore_222_rounds = 0 
		total_bore_44_rounds = 0 
		total_mm_7_rounds = 0
		total_mm_8_rounds = 0
		total_mm_9_rounds = 0
		total_mp_5_rounds = 0
		
		for center in centers:
			self.env.cr.execute("select count(*) as center_guards from hr_employee e, hr_guard g where g.id = e.guard_id and g.center_id = %s and current =True and is_guard = True"%center.id)
			p = self.env.cr.dictfetchall()[0]
			center_guards = p['center_guards']
		
			demands = self.env['sos.weapon.demand'].search([('center_id', '=', center.id),('date', '>=', date_from), ('date', '<=', date_to),('state', '<>', 'reject')])
			
			bore_32 = 0
			bore_30 = 0
			bore_12 = 0
			bore_222 = 0 
			bore_44 = 0 
			mm_7 = 0
			mm_8 = 0
			mm_9 = 0
			mp_5 = 0
			shilling = 0
		
			bore_32_rounds = 0
			bore_30_rounds = 0
			bore_12_rounds = 0
			bore_222_rounds = 0 
			bore_44_rounds = 0 
			mm_7_rounds = 0
			mm_8_rounds = 0
			mm_9_rounds = 0
			mp_5_rounds = 0
			
			for demand in demands:
				for d in demand.weapon_demand_line:
					if d.item_id.name == '32 Bore Pistol':
						bore_32 = bore_32 + (1 * d.qty)
					elif d.item_id.name == '30 Bore Pistol':
						bore_30 = bore_30 + (1 * d.qty)
					elif d.item_id.name == '12 Bore Pump Action':
						bore_12 = bore_12 + (1 * d.qty)
					elif d.item_id.name == '222 Bore Rifle':
						bore_222 = bore_222 + (1 * d.qty)
					elif d.item_id.name == '44 MM Rifle':
						bore_44 = bore_44 + (1 * d.qty)
					elif d.item_id.name == '7 MM Rifle':
						mm_7 = mm_7 + (1 * d.qty)
					elif d.item_id.name == '8 MM Rifle':
						mm_8 = mm_8 + (1 * d.qty)
					elif d.item_id.name == '9 MM':
						mm_9 = mm_9 + (1 * d.qty)
					elif d.item_id.name == 'MP-5 (Uzi Gun)':
						mp_5 = mp_5 + (1 * d.qty)
					elif d.item_id.name == 'Shilling':
						shilling = shilling + (1 * d.qty)
					elif d.item_id.name == '32 Bore Ammunition':
						bore_32_rounds = bore_32_rounds + (1 * d.qty)
					elif d.item_id.name == '30 Bore Ammunition':
						bore_30_rounds = bore_30_rounds + (1 * d.qty)
					elif d.item_id.name == '12 Bore Ammunition':
						bore_12_rounds = bore_12_rounds + (1 * d.qty)
					elif d.item_id.name == '222 Bore Ammunition':
						bore_222_rounds = bore_222_rounds + (1 * d.qty)
					elif d.item_id.name == '44 MM Ammunition':
						bore_44_rounds = bore_44_rounds + (1 * d.qty)
					elif d.item_id.name == '7 MM Ammunition':
						mm_7_rounds = mm_7_rounds + (1 * d.qty)
					elif d.item_id.name == '8 MM Ammunition':
						mm_8_rounds = mm_8_rounds + (1 * d.qty)
					elif d.item_id.name == '9 MM Ammunition':
						mm_9_rounds = mm_9_rounds + (1 * d.qty)
					
			res.append({
				'center_name' : center.name,
				'bore_32': 	bore_32 or '-',
				'bore_30' : 	bore_30 or '-',
				'bore_12': 	bore_12 or '-',
				'bore_222':	bore_222 or '-',
				'bore_44':	bore_44 or '-',
				'mm_7' :	mm_7 or '-',
				'mm_8' :	mm_8 or '-',
				'mm_9' : 	mm_9 or '-',
				'mp_5' : 	mp_5 or '-',
				'bore_32_rounds': 	bore_32_rounds or '-',
				'bore_30_rounds' : 	bore_30_rounds or '-',
				'bore_12_rounds': 	bore_12_rounds or '-',
				'bore_222_rounds':	bore_222_rounds or '-',
				'bore_44_rounds':	bore_44_rounds or '-',
				'mm_7_rounds':		mm_7_rounds or '-',
				'mm_8_rounds':		mm_8_rounds or '-',
				'mm_9_rounds': 		mm_9_rounds or '-',
				'mp_5_rounds': 		mp_5_rounds or '-',
				'shilling' : 		shilling or '-',
				'center_guards' : center_guards,
			
			})
			
			total_bore_32 += bore_32
			total_bore_30 += bore_30 
			total_bore_12 += bore_12 
			total_bore_222 += bore_222 
			total_bore_44 += bore_44 
			total_mm_7 += mm_7
			total_mm_8 += mm_8
			total_mm_9 += mm_9
			total_mp_5 += mp_5
			total_shilling += shilling
		
			total_bore_32_rounds += bore_32_rounds
			total_bore_30_rounds += bore_30_rounds
			total_bore_12_rounds += bore_12_rounds 
			total_bore_222_rounds += bore_222_rounds 
			total_bore_44_rounds += bore_44_rounds 
			total_mm_7_rounds += mm_7_rounds
			total_mm_8_rounds += mm_8_rounds 
			total_mm_9_rounds += mm_9_rounds 
			total_mp_5_rounds += mp_5_rounds 
			
						
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_weaponcenterall')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"Bore32" : total_bore_32,
			"Bore30" : total_bore_30,
			"Bore12" : total_bore_12,
			"Bore222" : total_bore_222,
			"Bore44" : total_bore_44,
			"MM7" : total_mm_7,
			"MM8" : total_mm_8,
			"MM9" : total_mm_9,
			"MP5" : total_mp_5,
			
			"Rounds32" : total_bore_32_rounds,
			"Rounds30" : total_bore_30_rounds,
			"Rounds12" : total_bore_12_rounds,
			"Rounds222" : total_bore_222_rounds,
			"Rounds44" : total_bore_44_rounds,
			"Rounds7" : total_mm_7_rounds,
			"Rounds8" : total_mm_8_rounds,
			"Rounds9" : total_mm_9_rounds,
			"Rounds5" : total_mp_5_rounds,
			
			"Shilling" : total_shilling,
			"get_date_formate" : self.get_date_formate,
		}
		
		
