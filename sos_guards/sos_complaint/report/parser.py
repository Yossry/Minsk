
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
import pdb
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


class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.localcontext.update({
			'random':random,
			'hello_world':self.hello_world,	
			'amount_in_word': self.amount_in_word,
			'get_totals': self.get_totals,
			'get_all_complaints': self.get_all_complaints,
			'get_all_project_complaints': self.get_all_project_complaints,			
			'get_serial': self.get_serial,
		})
		self.totals = AttrDict({'received':0,'solved':0,'unsolved':0,'serial':0})
		
	def get_serial(self):
		self.totals.serial = self.totals.serial+1
		return self.totals.serial
	
	def hello_world(self, name):
		return "Hello, %s!" % name
		
	def amount_in_word(self, amount_total):
		return amount_to_text(amount_total,'en','PKR')
	
	def get_all_complaints(self,form):
		res = []		
		
		start_date = form['start_date']
		end_date = form['end_date']
		order_by = form['order_by']
		
		filter_list = [('complaint_time','>=',start_date),('complaint_time','<=',end_date)]
		
		if form.get('project_ids',False):
			filter_list.append(('project_id','in',form.get('project_ids')))
		if form.get('center_ids',False):
			filter_list.append(('center_id','in',form.get('center_ids')))
		if form.get('coordinator_ids',False):
			filter_list.append(('coordinator_id','in',form.get('coordinator_ids')))
		if form.get('state',False):
			filter_list.append(('state','=',form.get('state')))
		
		complaint_obj = self.pool.get('sos.complaint')
		
		
		ids = complaint_obj.search(self.cr, self.uid, filter_list ,order = order_by )
		complaints = complaint_obj.browse(self.cr, self.uid,ids)	
		
		i = 1
		for complaint in complaints:
			complaint.serial = i
			i = i + 1
		
		
		return complaints
		
	def get_all_project_complaints(self,form):
		res = []		
				
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr, self.uid, [] )
		projects = project_obj.browse(self.cr, self.uid,project_ids)	
			
		start_date = form['start_date']
		end_date = form['end_date']
			
		i = 1
		for project in projects:
						
			self.cr.execute("select count(*) as received from sos_complaint where complaint_date >= %s and complaint_date <= %s and project_id = %s",(start_date,end_date,project.id))
			received = self.cr.dictfetchall()[0]
			
			self.cr.execute("select count(*) as solved from sos_complaint where state= 'done' and complaint_date >= %s and complaint_date <= %s and project_id = %s",(start_date,end_date,project.id))
			solved = self.cr.dictfetchall()[0]
			
			self.cr.execute("select count(*) as unsolved from sos_complaint where state <> 'done' and complaint_date >= %s and complaint_date <= %s and project_id = %s",(start_date,end_date,project.id))
			unsolved = self.cr.dictfetchall()[0]
			
			self.totals.received += int(0 if received['received'] is None else received['received'])
			self.totals.solved += int(0 if solved['solved'] is None else solved['solved'])
			self.totals.unsolved += int(0 if unsolved['unsolved'] is None else unsolved['unsolved'])
			
			res.append({
				'serial': i,
				'name': project.name,
				'received': received['received'],
				'solved': solved['solved'],
				'unsolved': unsolved['unsolved'],
			
			})
			i = i+1			
		
		return res
		
	def get_totals(self,code):		
		return self.totals[code]
