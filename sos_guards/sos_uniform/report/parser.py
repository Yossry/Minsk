
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
import pdb
from pytz import timezone
from openerp.tools.amount_to_text_en import amount_to_text
from openerp import tools
from datetime import datetime, timedelta
from openerp.tools.amount_to_text_en import amount_to_text


class AttrDict(dict):
	"""A dictionary with attribute-style access. It maps attribute access to the real dictionary.  """
	def __init__(self, init={}):
		dict.__init__(self, init)

	def __getstate__(self):
		return self.__dict__.items()

	def __setstate__(self, items):
		for key, val in items:
			self.__dict__[key] = val

	def __repr__(self):
		return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

	def __setitem__(self, key, value):
		return super(AttrDict, self).__setitem__(key, value)

	def __getitem__(self, name):
		item = super(AttrDict, self).__getitem__(name)
		return AttrDict(item) if type(item) == dict else item

	def __delitem__(self, name):
		return super(AttrDict, self).__delitem__(name)

	__getattr__ = __getitem__
	__setattr__ = __setitem__

	def copy(self):
		ch = AttrDict(self)
		return ch

class Parser(rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.localcontext.update({
			'random':random,
			'hello_world':self.hello_world,	
			'amount_in_word': self.amount_in_word,
			'get_serial' : self.get_serial,
			'get_date_formate': self.get_date_formate,
			'get_date_time' : self.get_date_time,
			'get_center_projects': self.get_center_projects,
			'get_project_centers':self.get_project_centers,
			'get_uniform_demands':self.get_uniform_demands,
			'get_centers':self.get_centers,
			'get_projects':self.get_projects,
			'get_uniform_item_totals':self.get_uniform_item_totals,
			'get_posts': self.get_posts,
			'get_safety_stock' : self.get_safety_stock,
			'get_totals':self.get_totals,
			'get_safety_stock_usage' : self.get_safety_stock_usage,
			'get_weapon_data' : self.get_weapon_data,
			'get_weapon_by_project' : self.get_weapon_by_project,
			'check_weapon_center' : self.check_weapon_center,
			'check_uniform_demand' : self.check_uniform_demand,
			'get_jacket_data' : self.get_jacket_data,
			'get_jacket_by_project' : self.get_jacket_by_project,
			'check_jacket_center' : self.check_jacket_center,
			'get_weapon_totals' : self.get_weapon_totals,
			'get_weapon_projects_totals' : self.get_weapon_projects_totals,
			'get_weapon_post_totals' : self.get_weapon_post_totals,
			'get_safety_data' : self.get_safety_data,
			'get_jacket_item_totals' : self.get_jacket_item_totals,
			'get_jacket_item_project_totals' : self.get_jacket_item_project_totals,
			'get_jacket_item_post_totals' : self.get_jacket_item_post_totals,
			'get_stationery_data' : self.get_stationery_data,
			'get_purchase_data' : self.get_purchase_data,
			
		})
		self.totals = AttrDict({'serial':0,'uniform_total':0,'shoe_total':0,'cap_total':0,'belt_total':0,
			'new_uniform_total':0,'new_shoe_total':0,'new_cap_total':0,'new_belt_total':0,'total':0,
			'bore_32_total':0,'bore_30_total':0,'bore_12_total':0,'bore_222_total':0,'bore_44_total':0,'mm_7_total':0,'mm_8_total':0,'mm_9_total':0,'shilling_total':0,'mp_5_total':0,
			'bore_32_rounds_total':0,'bore_30_rounds_total':0,'bore_12_rounds_total':0,'bore_222_rounds_total':0,'bore_44_rounds_total':0,'mm_7_rounds_total':0,'mm_8_rounds_total':0,'mm_9_rounds_total':0,'mp_5_rounds_total':0,})	
		
		
	def hello_world(self, name):
		return "Hello, %s!" % name
		
	def amount_in_word(self, amount_total):
		return amount_to_text(amount_total,'en','PKR')
		
	def get_serial(self):
		self.totals.serial = self.totals.serial+1
		return self.totals.serial
	
	def get_date_formate(self,sdate):        
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	def get_date_time(self):

		tz = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).partner_id.tz
		eastern = timezone(tz)
		loc_dt = datetime.now(eastern)

		fmt = '%A , %d.%m.%Y %H-%M %Z'
		return loc_dt.strftime(fmt)
		
		
	
	def get_center_projects(self, center_id):
		project_obj = self.pool.get('sos.project')
		self.cr.execute("select distinct project_id from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s"%center_id)
		rec_ids = self.cr.dictfetchall()
		
		project_ids = []
		for rec in rec_ids:
			project_ids.append(rec['project_id'])
			
		projects = project_obj.browse(self.cr,self.uid,project_ids)	
			
		return projects	
			
	def get_project_centers(self, project_id):
		center_obj = self.pool.get('sos.center')
		self.cr.execute("select distinct center_id from sos_post pp, res_partner p where pp.id = p.id and p.active = True and project_id = %s"%project_id)
		rec_ids = self.cr.dictfetchall()

		center_ids = []
		for rec in rec_ids:
			center_ids.append(rec['center_id'])	

		centers = center_obj.browse(self.cr,self.uid,center_ids)	
	
		return centers
		
		
	def get_centers(self):
		center_obj = self.pool.get('sos.center')
		ids = center_obj.search(self.cr,self.uid,[],order='name')
		centers = center_obj.browse(self.cr,self.uid,ids)
		return centers
	
	def get_projects(self):
		project_obj = self.pool.get('sos.project')
		ids = project_obj.search(self.cr,self.uid,[],order='name')
		projects = project_obj.browse(self.cr,self.uid,ids)
		return projects
		
		
	def get_posts(self,project_id,center_id):
		post_obj = self.pool.get('sos.post')
		ids = post_obj.search(self.cr,self.uid,[('project_id', '=', project_id), ('center_id', '=', center_id), ('active', '=', True)],order='name')
		posts = post_obj.browse(self.cr,self.uid,ids)
		return posts	
	
	def check_uniform_demand(self,data,center_id=None,project_id=None,post_id=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']	
		state = data['form']['state']	
		demand_obj = self.pool.get('sos.uniform.demand')

		dom = [('date', '>=', date_from), ('date', '<=', date_to)]
		if center_id:
			dom += [('center_id', '=', center_id)]
		if project_id:
			dom += [('project_id', '=', project_id)]
		if post_id:
			dom += [('post_id', '=', post_id)]

		if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
			dom += [('state', '=', state)]
		elif state == 'dispatch_deliver':
			dom += [('state', 'in', ['dispatch','done'])]	
		elif state == 'none_dispatched':
			dom += [('state', 'in', ['open','review','approve'])]
		elif state == 'all':
			dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
	
		demand_ids = demand_obj.search(self.cr,self.uid,dom)
		return demand_ids
	
	def get_uniform_demands(self,data,center_id=None,project_id=None,post_id=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']	
		state = data['form']['state']	
		demand_obj = self.pool.get('sos.uniform.demand')

		dom = [('date', '>=', date_from), ('date', '<=', date_to)]
		if center_id:
			dom += [('center_id', '=', center_id)]
		if project_id:
			dom += [('project_id', '=', project_id)]
		if post_id:
			dom += [('post_id', '=', post_id)]

		if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
			dom += [('state', '=', state)]
		elif state == 'dispatch_deliver':
			dom += [('state', 'in', ['dispatch','done'])]	
		elif state == 'none_dispatched':
			dom += [('state', 'in', ['open','review','approve'])]
		elif state == 'all':
			dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
	
		demand_ids = demand_obj.search(self.cr,self.uid,dom)
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		return demands

	def get_uniform_item_totals(self,data,center_id=None,project_id=None,post_id=None):		
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']	
		state = data['form']['state']	
		demand_obj = self.pool.get('sos.uniform.demand')

		dom = [('date', '>=', date_from), ('date', '<=', date_to)]
		if center_id:
			dom += [('center_id', '=', center_id)]
			guards = len(self.pool.get('hr.employee').search(self.cr,self.uid,[('current','=',True),('is_guard','=',True),('center_id','=',center_id)]))
		elif project_id:
			dom += [('project_id', '=', project_id)]
			guards = len(self.pool.get('hr.employee').search(self.cr,self.uid,[('current','=',True),('is_guard','=',True),('project_id','=',project_id)]))
		elif post_id:
			dom += [('post_id', '=', post_id)]
			guards = len(self.pool.get('hr.employee').search(self.cr,self.uid,[('current','=',True),('is_guard','=',True),('current_post_id','=',post_id)]))

		if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
			dom += [('state', '=', state)]
		elif state == 'dispatch_deliver':
			dom += [('state', 'in', ['dispatch','done'])]	
		elif state == 'none_dispatched':
			dom += [('state', 'in', ['open','review','approve'])]
		elif state == 'all':
			dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
	
		demand_ids = demand_obj.search(self.cr,self.uid,dom)
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)

		res = []
		uniform = 0
		shoe = 0
		cap = 0
		belt = 0
		new_uniform = 0
		new_shoe = 0
		new_cap = 0
		new_belt = 0
		total = 0
		
		for demand in demands:
			if demand.is_new_post:
				for d in demand.uniform_demand_line:
					if d.item_id.name == 'Uniform':
						new_uniform = new_uniform + (1 * d.qty)
					elif d.item_id.name == 'Cap':
						new_cap = new_cap + (1 * d.qty)
					elif d.item_id.name == 'Belt':
						new_belt = new_belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe':
						new_shoe = new_shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Shoes':
						unew_niform = new_uniform + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Belt-Cap':
						new_cap = new_cap + (1 * d.qty)
						new_uniform = new_uniform + (1 * d.qty)
						new_belt = new_belt + (1 * d.qty)
					elif d.item_id.name == 'Belt-Cap':
						new_cap = new_cap + (1 * d.qty)
						new_belt = new_belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe-Belt-Cap':
						new_cap = new_cap + (1 * d.qty)
						new_belt = new_belt + (1 * d.qty)	
						new_shoe = new_shoe + (1 * d.qty)

					elif d.item_id.name == 'New Deployment Kit':
						new_cap = new_cap + (1 * d.qty)
						new_belt = new_belt + (1 * d.qty)
						new_shoe = new_shoe + (1 * d.qty)
						new_uniform = new_uniform + (2 * d.qty)
						
					elif d.item_id.name == 'Complete Kit':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
						uniform = uniform + (1 * d.qty)	
			else:
				for d in demand.uniform_demand_line:
					if d.item_id.name == 'Uniform':
						uniform = uniform + (1 * d.qty)
					elif d.item_id.name == 'Cap':
						cap = cap + (1 * d.qty)
					elif d.item_id.name == 'Belt':
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe':
						shoe = shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Shoes':
						uniform = uniform + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Belt-Cap':
						cap = cap + (1 * d.qty)
						uniform = uniform + (1 * d.qty)
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Belt-Cap':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe-Belt-Cap':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)	
						shoe = shoe + (1 * d.qty)

					elif d.item_id.name == 'New Deployment Kit':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
						uniform = uniform + (2 * d.qty)
					elif d.item_id.name == 'Complete Kit':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
						uniform = uniform + (1 * d.qty)
						
			total = uniform + shoe + belt + cap + new_uniform + new_shoe + new_belt + new_cap
		self.totals.uniform_total = self.totals.uniform_total + uniform
		self.totals.shoe_total = self.totals.shoe_total + shoe
		self.totals.belt_total = self.totals.belt_total + belt
		self.totals.cap_total = self.totals.cap_total + cap
		
		self.totals.new_uniform_total = self.totals.new_uniform_total + new_uniform
		self.totals.new_shoe_total = self.totals.new_shoe_total + new_shoe
		self.totals.new_belt_total = self.totals.new_belt_total + new_belt
		self.totals.new_cap_total = self.totals.new_cap_total + new_cap
		
		
		res.append({
			'uniform': uniform or '-',
			'shoe': shoe or '-',
			'cap': cap or '-',
			'belt': belt or '-',
			'new_uniform': new_uniform or '-',
			'new_shoe': new_shoe or '-',
			'new_belt': new_belt or '-',
			'new_cap': new_cap or '-',
			'total' : total or '-',
			'guards' : guards,
		})			
		return res
		
		
	def get_safety_stock(self,data,center_id):
	
		#self.totals = AttrDict({'uniform_total':0,'shoe_total':0,'cap_total':0,'belt_total':0})
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.uniform.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('demand_type', '=', 'safety'),('date', '>=', start_date), ('date', '<=', end_date)])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		res = []
		uniform = 0
		shoe = 0
		cap = 0
		belt = 0
		
		for demand in demands:
			for d in demand.uniform_demand_line:
				if d.item_id.name == 'Uniform':
					uniform = uniform + (1 * d.qty)
				elif d.item_id.name == 'Cap':
					cap = cap + (1 * d.qty)
				elif d.item_id.name == 'Belt':
					belt = belt + (1 * d.qty)
				elif d.item_id.name == 'Shoe':
					shoe = shoe + (1 * d.qty)
				elif d.item_id.name == 'Uniform-Shoes':
					uniform = uniform + (1 * d.qty)
					shoe = shoe + (1 * d.qty)
				elif d.item_id.name == 'Uniform-Belt-Cap':
					cap = cap + (1 * d.qty)
					uniform = uniform + (1 * d.qty)
					belt = belt + (1 * d.qty)
				elif d.item_id.name == 'Belt-Cap':
					cap = cap + (1 * d.qty)
					belt = belt + (1 * d.qty)
				elif d.item_id.name == 'Shoe-Belt-Cap':
					cap = cap + (1 * d.qty)
					belt = belt + (1 * d.qty)	
					shoe = shoe + (1 * d.qty)
					
				elif d.item_id.name == 'New Deployment Kit':
					cap = cap + (1 * d.qty)
					belt = belt + (1 * d.qty)
					shoe = shoe + (1 * d.qty)
					uniform = uniform + (2 * d.qty)
				elif d.item_id.name == 'Complete Kit':
					cap = cap + (1 * d.qty)
					belt = belt + (1 * d.qty)
					shoe = shoe + (1 * d.qty)
					uniform = uniform + (1 * d.qty)
		
		self.totals.uniform_total = self.totals.uniform_total + uniform
		self.totals.shoe_total = self.totals.shoe_total + shoe
		self.totals.belt_total = self.totals.belt_total + belt
		self.totals.cap_total = self.totals.cap_total + cap
		
		
		res.append({
			'uniform': uniform,
			'shoe': shoe,
			'cap': cap,
			'belt': belt
		})			
		return res	
		
		
	def get_safety_stock_usage(self,data,center_id):
	
		#self.totals = AttrDict({'uniform_total':0,'shoe_total':0,'cap_total':0,'belt_total':0})
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.uniform.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('demand_type', '=', 'safety'),('date', '>=', start_date), ('date', '<=', end_date)])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		res = []
		uniform = 0
		shoe = 0
		cap = 0
		belt = 0
		
		for demand in demands:
		
			for d in demand.uniform_demand_line:
				if d.action == 'safety':
					if d.item_id.name == 'Uniform':
						uniform = uniform + (1 * d.qty)
					elif d.item_id.name == 'Cap':
						cap = cap + (1 * d.qty)
					elif d.item_id.name == 'Belt':
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe':
						shoe = shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Shoes':
						uniform = uniform + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
					elif d.item_id.name == 'Uniform-Belt-Cap':
						cap = cap + (1 * d.qty)
						uniform = uniform + (1 * d.qty)
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Belt-Cap':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
					elif d.item_id.name == 'Shoe-Belt-Cap':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)	
						shoe = shoe + (1 * d.qty)

					elif d.item_id.name == 'New Deployment Kit':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
						uniform = uniform + (2 * d.qty)
					elif d.item_id.name == 'Complete Kit':
						cap = cap + (1 * d.qty)
						belt = belt + (1 * d.qty)
						shoe = shoe + (1 * d.qty)
						uniform = uniform + (1 * d.qty)	
		
		self.totals.uniform_total = self.totals.uniform_total + uniform
		self.totals.shoe_total = self.totals.shoe_total + shoe
		self.totals.belt_total = self.totals.belt_total + belt
		self.totals.cap_total = self.totals.cap_total + cap
		
		
		res.append({
			'uniform': uniform,
			'shoe': shoe,
			'cap': cap,
			'belt': belt
		})			
		return res
		
		
	def get_weapon_data(self,data):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		weapon_obj = self.pool.get('sos.weapon.demand')
		weapon_ids = weapon_obj.search(self.cr,self.uid,[('date', '>=', from_date),('date','<=',to_date), ('state', '<>', 'reject')],order='date,center_id, post_id')
		weapons = weapon_obj.browse(self.cr,self.uid,weapon_ids)
		return weapons
		
	def get_weapon_by_project(self,project_id,center_id,data):
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		weapon_obj = self.pool.get('sos.weapon.demand')
		ids = weapon_obj.search(self.cr,self.uid,[('project_id', '=', project_id),('center_id', '=', center_id),('date', '>=', start_date),('date','<=', end_date),('state', '<>', 'reject')],order='date,center_id, post_id')
		weapons = weapon_obj.browse(self.cr,self.uid,ids)
		return weapons
		
		
	def get_weapon_totals(self,data,center_id):
	
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.weapon.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('date', '>=', start_date), ('date', '<=', end_date),('state', '<>', 'reject')])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		
		
		self.cr.execute("select count(*) as center_guards from hr_employee e, hr_guard g where g.id = e.guard_id and g.center_id = %s and current =True and is_guard = True "%center_id)
		c = self.cr.dictfetchall()[0]
		center_guards = c['center_guards']
		
		res = []
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
					
		self.totals.bore_32_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_total = self.totals.mp_5_total + mp_5
		
		self.totals.bore_32_rounds_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_rounds_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_rounds_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_rounds_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_rounds_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_rounds_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_rounds_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_rounds_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_rounds_total = self.totals.mp_5_total + mp_5
		
		self.totals.shilling_total = self.totals.shilling_total + shilling
		
		res.append({
			'bore_32': 	bore_32,
			'bore_30' : 	bore_30,
			'bore_12': 	bore_12,
			'bore_222':	bore_222,
			'bore_44':	bore_44,
			'mm_7' :	mm_7,
			'mm_8' :	mm_8,
			'mm_9' : 	mm_9,
			'mp_5' : 	mp_5,
			'bore_32_rounds': 	bore_32_rounds,
			'bore_30_rounds' : 	bore_30_rounds,
			'bore_12_rounds': 	bore_12_rounds,
			'bore_222_rounds':	bore_222_rounds,
			'bore_44_rounds':	bore_44_rounds,
			'mm_7_rounds':		mm_7_rounds,
			'mm_8_rounds':		mm_8_rounds,
			'mm_9_rounds': 		mm_9_rounds,
			'mp_5_rounds': 		mp_5_rounds,
			'shilling' : 		shilling,
			'center_guards' : center_guards,
			
		})			
		return res
		
		
	def get_weapon_projects_totals(self,data,project_id):
	
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.weapon.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('project_id', '=', project_id),('date', '>=', start_date), ('date', '<=', end_date),('state', '<>', 'reject')])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		
		
		self.cr.execute("select count(*) as project_guards from hr_employee e, hr_guard g where g.id = e.guard_id and g.project_id = %s and current =True and is_guard = True"%project_id)
		p = self.cr.dictfetchall()[0]
		project_guards = p['project_guards']
		
		res = []
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
					
		self.totals.bore_32_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_total = self.totals.mp_5_total + mp_5
		
		self.totals.bore_32_rounds_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_rounds_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_rounds_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_rounds_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_rounds_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_rounds_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_rounds_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_rounds_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_rounds_total = self.totals.mp_5_total + mp_5
		
		self.totals.shilling_total = self.totals.shilling_total + shilling
		
		res.append({
			'bore_32': 	bore_32,
			'bore_30' : 	bore_30,
			'bore_12': 	bore_12,
			'bore_222':	bore_222,
			'bore_44':	bore_44,
			'mm_7' :	mm_7,
			'mm_8' :	mm_8,
			'mm_9' : 	mm_9,
			'mp_5' : 	mp_5,
			'bore_32_rounds': 	bore_32_rounds,
			'bore_30_rounds' : 	bore_30_rounds,
			'bore_12_rounds': 	bore_12_rounds,
			'bore_222_rounds':	bore_222_rounds,
			'bore_44_rounds':	bore_44_rounds,
			'mm_7_rounds':		mm_7_rounds,
			'mm_8_rounds':		mm_8_rounds,
			'mm_9_rounds': 		mm_9_rounds,
			'mp_5_rounds': 		mp_5_rounds,
			'shilling' : 		shilling,
			'project_guards' : project_guards,
			
		})			
		return res
		
		
	def get_weapon_post_totals(self,data,post_id):
	
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.weapon.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('post_id', '=', post_id),('date', '>=', start_date), ('date', '<=', end_date),('state', '<>', 'reject')])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		
		res = []
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
					
		self.totals.bore_32_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_total = self.totals.mp_5_total + mp_5
		
		self.totals.bore_32_rounds_total = self.totals.bore_32_total + bore_32
		self.totals.bore_30_rounds_total = self.totals.bore_30_total + bore_30
		self.totals.bore_12_rounds_total = self.totals.bore_12_total + bore_12
		self.totals.bore_222_rounds_total = self.totals.bore_222_total + bore_222
		self.totals.bore_44_rounds_total = self.totals.bore_44_total + bore_44
		self.totals.mm_7_rounds_total = self.totals.mm_7_total + mm_7
		self.totals.mm_8_rounds_total = self.totals.mm_8_total + mm_8
		self.totals.mm_9_rounds_total = self.totals.mm_9_total + mm_9
		self.totals.mp_5_rounds_total = self.totals.mp_5_total + mp_5
		
		self.totals.shilling_total = self.totals.shilling_total + shilling
		
		res.append({
			'bore_32': 	bore_32,
			'bore_30' : 	bore_30,
			'bore_12': 	bore_12,
			'bore_222':	bore_222,
			'bore_44':	bore_44,
			'mm_7' :	mm_7,
			'mm_8' :	mm_8,
			'mm_9' : 	mm_9,
			'mp_5' : 	mp_5,
			'bore_32_rounds': 	bore_32_rounds,
			'bore_30_rounds' : 	bore_30_rounds,
			'bore_12_rounds': 	bore_12_rounds,
			'bore_222_rounds':	bore_222_rounds,
			'bore_44_rounds':	bore_44_rounds,
			'mm_7_rounds':		mm_7_rounds,
			'mm_8_rounds':		mm_8_rounds,
			'mm_9_rounds': 		mm_9_rounds,
			'mp_5_rounds': 		mp_5_rounds,
			'shilling' : 		shilling,
			
		})			
		return res		
		
		
	def check_weapon_center(self,data,center_id,project_id):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		weapon_obj = self.pool.get('sos.weapon.demand')
		ids = weapon_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('project_id', '=', project_id),('date', '>=', from_date),('date','<=', to_date),('state', '<>', 'rejected')])
		weapons = weapon_obj.browse(self.cr,self.uid,ids)
		return weapons
		
	
		
	def get_jacket_data(self,data):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		jacket_obj = self.pool.get('sos.jacket.demand')
		jacket_ids = jacket_obj.search(self.cr,self.uid,[('date', '>=', from_date),('date','<=',to_date), ('state', '<>', 'rejected')],order='date,center_id, post_id')
		jackets = jacket_obj.browse(self.cr,self.uid,jacket_ids)
		return jackets
		
	def get_jacket_by_project(self,project_id,center_id,data):
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		jacket_obj = self.pool.get('sos.jacket.demand')
		ids = jacket_obj.search(self.cr,self.uid,[('project_id', '=', project_id),('center_id', '=', center_id),('date', '>=', start_date),('date','<=', end_date),('state', '<>', 'rejected')],order='date')
		jackets = jacket_obj.browse(self.cr,self.uid,ids)
		return jackets
		
	def check_jacket_center(self,data,center_id,project_id):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		jacket_obj = self.pool.get('sos.jacket.demand')
		ids = jacket_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('project_id', '=', project_id),('date', '>=', from_date),('date','<=', to_date),('state', '<>', 'rejected')])
		jackets = jacket_obj.browse(self.cr,self.uid,ids)
		return jackets
		
	def get_safety_data(self,data):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		safety_obj = self.pool.get('sos.safety.demand')
		safety_ids = safety_obj.search(self.cr,self.uid,[('date', '>=', from_date),('date','<=',to_date), ('state', '<>', 'rejected')],order='date,center_id')
		safety = safety_obj.browse(self.cr,self.uid,safety_ids)
		return safety
		
	def get_jacket_item_totals(self,data,center_id):
	
		start_date = data['form']['date_from']
		end_date = data['form']['date_to']
		
		demand_obj = self.pool.get('sos.jacket.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('date', '>=', start_date), ('date', '<=', end_date)])
		
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)
		center_guards = len(self.pool.get('hr.employee').search(self.cr,self.uid,[('center_id', '=', center_id),('current', '=', True), ('is_guard', '=', True)]))
		
		res = []
		jacket = 0
		jersey = 0
		rain_coat = 0
		new_jacket = 0
		new_jersey = 0
		new_rain_coat = 0
		total = 0
		
		
		for demand in demands:
			if demand.new_posts:
				for d in demand.jacket_demand_line:
					if d.item == 'jersey':
						new_jersey = new_jersey + (1 * d.qty)
					elif d.item == 'jacket':
						new_jacket = new_jacket + (1 * d.qty)
					elif d.item == 'raincoat':
						new_rain_coat = new_rain_coat + (1 * d.qty)
			else:
				for d in demand.jacket_demand_line:
					if d.item == 'jersey':
						jersey = jersey + (1 * d.qty)
					elif d.item == 'jacket':
						jacket = jacket + (1 * d.qty)
					elif d.item == 'raincoat':
						rain_coat =rain_coat + (1 * d.qty)
						
			total = jersey + jacket + rain_coat + new_jersey + new_jacket + new_rain_coat
		self.totals.uniform_total = self.totals.uniform_total + jacket
		self.totals.shoe_total = self.totals.shoe_total + jersey
		self.totals.belt_total = self.totals.belt_total + rain_coat
		
		self.totals.new_uniform_total = self.totals.new_uniform_total + new_jacket
		self.totals.new_shoe_total = self.totals.new_shoe_total + new_jersey
		self.totals.new_belt_total = self.totals.new_belt_total + new_rain_coat
		
		
		res.append({
			'jacket': jacket,
			'jersey': jersey,
			'rain_coat': rain_coat,
			'new_jacket': new_jacket,
			'new_jersey': new_jersey,
			'new_rain_coat': new_rain_coat,
			'total' : total,
			'center_guards' : center_guards,
		})			
		return res
	
	def get_jacket_item_project_totals(self,data,project_id):
		
			start_date = data['form']['date_from']
			end_date = data['form']['date_to']
			
			demand_obj = self.pool.get('sos.jacket.demand')
			demand_ids = demand_obj.search(self.cr,self.uid,[('project_id', '=', project_id),('date', '>=', start_date), ('date', '<=', end_date)])
			demands = demand_obj.browse(self.cr,self.uid,demand_ids)
			
			project_guards = len(self.pool.get('hr.employee').search(self.cr,self.uid,[('project_id', '=', project_id),('current', '=', True), ('is_guard', '=', True)]))
			
			res = []
			jacket = 0
			jersey = 0
			rain_coat = 0
			new_jacket = 0
			new_jersey = 0
			new_rain_coat = 0
			total = 0
			
			
			for demand in demands:
				if demand.new_posts:
					for d in demand.jacket_demand_line:
						if d.item == 'jersey':
							new_jersey = new_jersey + (1 * d.qty)
						elif d.item == 'jacket':
							new_jacket = new_jacket + (1 * d.qty)
						elif d.item == 'raincoat':
							new_rain_coat = new_rain_coat + (1 * d.qty)
				else:
					for d in demand.jacket_demand_line:
						if d.item == 'jersey':
							jersey = jersey + (1 * d.qty)
						elif d.item == 'jacket':
							jacket = jacket + (1 * d.qty)
						elif d.item == 'raincoat':
							rain_coat =rain_coat + (1 * d.qty)
							
				total = jersey + jacket + rain_coat + new_jersey + new_jacket + new_rain_coat
			self.totals.uniform_total = self.totals.uniform_total + jacket
			self.totals.shoe_total = self.totals.shoe_total + jersey
			self.totals.belt_total = self.totals.belt_total + rain_coat
			
			self.totals.new_uniform_total = self.totals.new_uniform_total + new_jacket
			self.totals.new_shoe_total = self.totals.new_shoe_total + new_jersey
			self.totals.new_belt_total = self.totals.new_belt_total + new_rain_coat
			
			
			res.append({
				'jacket': jacket,
				'jersey': jersey,
				'rain_coat': rain_coat,
				'new_jacket': new_jacket,
				'new_jersey': new_jersey,
				'new_rain_coat': new_rain_coat,
				'total' : total,
				'project_guards' : project_guards,
			})			
			return res
			
			
	def get_jacket_item_post_totals(self,data,post_id):

		start_date = data['form']['date_from']
		end_date = data['form']['date_to']

		demand_obj = self.pool.get('sos.jacket.demand')
		demand_ids = demand_obj.search(self.cr,self.uid,[('post_id', '=', post_id),('date', '>=', start_date), ('date', '<=', end_date)])
		demands = demand_obj.browse(self.cr,self.uid,demand_ids)


		res = []
		jacket = 0
		jersey = 0
		rain_coat = 0
		new_jacket = 0
		new_jersey = 0
		new_rain_coat = 0
		total = 0


		for demand in demands:
			if demand.new_posts:
				for d in demand.jacket_demand_line:
					if d.item == 'jersey':
						new_jersey = new_jersey + (1 * d.qty)
					elif d.item == 'jacket':
						new_jacket = new_jacket + (1 * d.qty)
					elif d.item == 'raincoat':
						new_rain_coat = new_rain_coat + (1 * d.qty)
			else:
				for d in demand.jacket_demand_line:
					if d.item == 'jersey':
						jersey = jersey + (1 * d.qty)
					elif d.item == 'jacket':
						jacket = jacket + (1 * d.qty)
					elif d.item == 'raincoat':
						rain_coat =rain_coat + (1 * d.qty)

			total = jersey + jacket + rain_coat + new_jersey + new_jacket + new_rain_coat
		self.totals.uniform_total = self.totals.uniform_total + jacket
		self.totals.shoe_total = self.totals.shoe_total + jersey
		self.totals.belt_total = self.totals.belt_total + rain_coat

		self.totals.new_uniform_total = self.totals.new_uniform_total + new_jacket
		self.totals.new_shoe_total = self.totals.new_shoe_total + new_jersey
		self.totals.new_belt_total = self.totals.new_belt_total + new_rain_coat


		res.append({
			'jacket': jacket,
			'jersey': jersey,
			'rain_coat': rain_coat,
			'new_jacket': new_jacket,
			'new_jersey': new_jersey,
			'new_rain_coat': new_rain_coat,
			'total' : total,
		})			
		return res
		
	def get_stationery_data(self,data):
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		
		stat_obj = self.pool.get('sos.stationery.demand')
		stat_ids = stat_obj.search(self.cr,self.uid,[('date', '>=', from_date),('date','<=',to_date), ('state', '<>', 'rejected')],order='date,center_id')
		stats = stat_obj.browse(self.cr,self.uid,stat_ids)
		return stats
		
		
	def get_purchase_data(self,data):
	
		from_date = data['form']['date_from']
		to_date = data['form']['date_to']
		categ_id = data['form']['categ_id'][0]
		
		purchase_obj = self.pool.get('stock.move')
		purchase_ids = purchase_obj.search(self.cr,self.uid,[('date', '>=', from_date),('date','<=',to_date),('product_id.product_tmpl_id.categ_id.id', '=',categ_id ),('location_dest_id', '=', 12)],order='date,product_id')
		purchases = purchase_obj.browse(self.cr,self.uid,purchase_ids)
		return purchases	
		
	def get_totals(self,code):		
		return self.totals[code]
			
					
					
					
					
					
		

	
	
	
