import pdb
import time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import itertools

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()
	
def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
	   
def dateToStr(ddate):
	return ddate.strftime('%Y-%m-%d')
			
def datetimeToStr(ddate):
	return ddate.strftime('%Y-%m-%d %H:%M:%S')

def utcDate(self, ddate):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_date = local_tz.localize(ddate, is_dst=False)
	utc_date = local_date.astimezone(utc)
	return utc_date
	
def localDate(self, utc_dt):
    user = self.env.user
    local_tz = timezone(user.tz)
    local_dt = utc_dt.replace(tzinfo=utc).astimezone(local_tz)
    return local_dt		

class sos_guard_action_reason(models.Model):
	_name = "sos.guard.action.reason"
	_description = "Action Reason"
	
	name = fields.Char('Reason', size=64, required=True, help='Specifie the reason.')        


class sos_guard_replacement(models.Model):
	_name = "sos.guard.replacement"
	_description = "Guard Replacement"
	_order = 'name desc'

	name = fields.Date('From Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	name2 = fields.Date('To Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', required=True,string = 'Project')
	center_id = fields.Many2one('sos.center','Center', required=True)
	post_id = fields.Many2one('sos.post', string = 'Post', required=True,domain=[('active','=',True)])
	description = fields.Char("Description", size=128, help='Specifie the reason.')
	employee_id1 = fields.Many2one('hr.employee', "Original Guard", domain=[('is_guard','=',True),('current','=',True)], required=True)             
	employee_id2 = fields.Many2one('hr.employee', "Replaced By", domain=[('is_guard','=',True),('current','=',True)], required=True)             
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',default='draft')
	
	@api.one
	def action_replacement_done(self):
		att_obj = self.env['sos.guard.attendance']
		
		dStart = datetime.strptime(self.name, '%Y-%m-%d').date()
		dEnd = datetime.strptime(self.name2, '%Y-%m-%d').date()
		while dStart <= dEnd:
			att_ids = att_obj.search([('state','!=','done'), ('employee_id', '=', self.employee_id1.id),('name','=',dStart)])	
			if att_ids:
				att_ids.write({'action':'absent'})		

			att_obj.create({
				'project_id': self.project_id.id,
				'post_id': self.post_id.id,
				'center_id': self.center_id.id,
				'name': dStart,
				'employee_id': self.employee_id2.id,
				'action': 'extra',					
				'state': 'draft',
			})		
			dStart = dStart + relativedelta(days=+1)

		self.state = 'done'


class sos_guard_shortfall(models.Model):
	_name = "sos.guard.shortfall"
	_description = "Short Fall"
	_order = 'name desc'

	name = fields.Date('From Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	name2 = fields.Date('To Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', required=True,string = 'Project')
	center_id = fields.Many2one('sos.center','Center', required=True)
	post_id = fields.Many2one('sos.post', string = 'Post', required=True,domain=[('active','=',True)])
	description = fields.Char("Description", size=128, help='Specifie the reason.')
	employee_id = fields.Many2one('hr.employee', "Employee", domain=[('is_guard','=',True),('current','=',True)], required=True)             
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',default='draft')        
	
	@api.one
	def action_shortfall_done(self):
		att_obj = self.env['sos.guard.attendance']
		dStart = datetime.strptime(self.name, '%Y-%m-%d').date()
		dEnd = datetime.strptime(self.name2, '%Y-%m-%d').date()
		while dStart <= dEnd:
			att_ids = att_obj.search([('state','!=','done'),('employee_id', '=', self.employee_id.id),('name','=',dStart)])	
			if att_ids:
				att_ids.write({'action':'absent'})		
			dStart = dStart + relativedelta(days=+1)

		self.state = 'done'


class sos_center_attendance(models.Model):
	_name = "sos.center.attendance"
	_description = "Center Attendance"
	_order = 'id desc'

	name = fields.Date('Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	center_id = fields.Many2one('sos.center','Center', required=True)
	state = fields.Selection([('draft','Draft'),('marked','Marked'),('verified','Verified'),('done','Done')],'Status',default='draft')
	att_mark_count = fields.Integer('Marked Attendance')

	@api.model
	def mark_center_attendance_cron(self,date_att=False):		
		centers = self.env['sos.center'].search([])		
		if not date_att:
			date_att = fields.Date.context_today(self)
		for center in centers:		
			att_ids = self.search([('name','=',date_att),('center_id','=',center.id)])
			if not att_ids:
				vals = {
					'name': date_att,
					'center_id': center.id,
					'state': 'draft',
				}
				self.create(vals)

	@api.model
	def mark_guards_attendance_cron(self,nlimit=1):		
		att_pool = self.env['sos.guard.attendance']
		shortfall_pool = self.env['sos.guard.shortfall']
		replacement_pool = self.env['sos.guard.replacement']
		duty_pool = self.env['sos.guard.post']
		
		center_att_ids = self.search([('state','=','draft')],limit=nlimit)	
		#self._context['attendance_cron_running'] = True

		for center_att_id in center_att_ids:		
			name = center_att_id.name 
			
			args = [('current','=',True)]	
			center_id = center_att_id.center_id.id
			args.append(('post_id.center_id','=', center_id))
			args.append(('guard_id.appointmentdate','<=', name))
				
			ids1 = duty_pool.search(args)
			total = len(ids1)
			cnt = 0
			for guard_duty in ids1:
				att_action = 'present'				
								
				short_id = shortfall_pool.search([('name','=',name),('employee_id','=',guard_duty.employee_id.id)])
				if short_id:
					att_action = 'absent'
				
				replacement_id = replacement_pool.search([('name','=',name),('employee_id1','=',guard_duty.employee_id.id)])
				if replacement_id:
					att_action = 'absent'
			
			
				att_id = att_pool.search([('name','=',name),('action','=',att_action),('employee_id','=',guard_duty.employee_id.id)])
				if not att_id:
					if (guard_duty.project_id and guard_duty.post_id):
						vals = {
							'project_id': guard_duty.project_id.id,
							'post_id': guard_duty.post_id.id,
							'center_id': guard_duty.post_id.center_id.id,
							'name': name,
							'paidon': guard_duty.post_id.paidon,
							'employee_id': guard_duty.employee_id.id,
							'action': att_action,
							'state': 'draft',
							'shift' : 'morning',
						}										
						rec_id = att_pool.create(vals)
						cnt = cnt + 1
			center_att_id.att_mark_count = cnt
			center_att_id.state = 'marked'	 
		#self._context['attendance_cron_running'] = False
		#self._update_cron()

	@api.model	
	def _update_cron(self):
		#if self._context.get('attendance_cron_running',False):
		#	return
		
		try:
			cron = self.env['ir.model.data'].sudo().get_object('sos_payroll', 'sos_mark_guards_attendance')
		except ValueError:
			return

		cron.toggle(model=self._name, domain=[('state','=','draft')])

	@api.model	
	def create(self,values):
		res = super(sos_center_attendance, self).create(values)
		self._update_cron()
		return res  

	@api.multi
	def write(self, values):
		res = super(sos_center_attendance, self).write(values)
		self._update_cron()
		return res

	@api.multi
	def unlink(self):
		res = super(sos_center_attendance, self).unlink()
		self._update_cron()
		return res         		


class sos_guard_attendance(models.Model):
	_name = "sos.guard.attendance"
	_description = "Attendance"
	_order = 'id desc'

	name = fields.Date('Date', required=True,index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', required=True,string = 'Project',index=True)
	center_id = fields.Many2one('sos.center','Center',index=True)
	post_id = fields.Many2one('sos.post', string = 'Post', required=True,domain=[('active','=',True)],index=True)
	action = fields.Selection([('present', 'Present'), ('absent', 'Absent'), ('leave', 'Leave'), ('double','Double'),('extra','Extra'),('extra_double','Extra Double')], 'Action', required=True)
	action_desc = fields.Many2one("sos.guard.action.reason", "Action Reason", help='Specifie the reason.')
	employee_id = fields.Many2one('hr.employee', "Employee", domain=[('is_guard','=',True),('current','=',True)],index=True)             
	state = fields.Selection([('draft','Draft'),('counted','Counted'),('done','Done')],'Status')
	paidon = fields.Boolean(_related='post_id.paidon', string='Paid On', store=True,)
	slip_id = fields.Many2one('guards.payslip', "Pay Slip")
	shift = fields.Selection([('morning','Morning'),('night','Night')],'Shift')

	@api.one	
	def unlink(self):
		slip_obj = self.pool.get('guards.payslip')
		att_log_obj = self.env['sos.attendance.log']
		
		if self.slip_id and self.slip_id.move_id:
			raise UserError(('You can not delete attendance of Employess Days for which Salary have been Finalized.'))
			
		slip = self.slip_id
		if slip:
			date_from = slip.date_from
			date_to = slip.date_to
			employee_id = slip.employee_id.id
			paidon = slip.paidon
			contract_id = slip.contract_id.id
		
		## Creating Entry in att. log	
		res = {
			'name' : self.name,
			'project_id' : self.project_id.id,
			'center_id' : self.center_id.id,
			'post_id' : self.post_id.id,
			'employee_id' : self.employee_id.id,
			'action' : self.action,
			'state' : self.state,
			'user_id' : self.env.user.id, 
			}
			
		att_log_obj.sudo().create(res)
		
		ret = super(sos_guard_attendance, self).unlink()
					
		return ret
		
class hr_guard(models.Model):
	_inherit ='hr.guard'
	_description ="Guard Employee"

	
	#@api.one
	#@api.depends('attendance_ids')
	#0def _check_draft_attendance(self):
	#	Attendance = self.env['sos.guard.attendance']
	#	employee = self.env['hr.employee'].search([('guard_id','=',self.id)])
	#	pending_projects = self.env['project.salary.pending'].sudo().search([('state', '=','block')])
	#	set2 = Attendance.search([('name', '<=', '2010-01-01')])	
	#	for rec in pending_projects:
	#		set2 = set2 | Attendance.search([('name', '>=', rec.date_from), ('name', '<=', rec.date_to), ('employee_id', '=', employee.id), ('project_id', '=', rec.project_id.id),('slip_id','=',False)])	
	#		
	#	att_ids = Attendance.search([('employee_id', '=', employee.id),('slip_id','=',False)]) 
	#	self.att_draft = (att_ids - set2) and True or False
		
	@api.one
	def _shortfall_count(self):
		employee = self.env['hr.employee'].search([('guard_id','=',self.id)])
		self.shortfall_count = self.env['sos.guard.shortfall'].search_count([('employee_id', '=', employee.id)])
		
	@api.one
	def _replacement_count(self):
		employee = self.env['hr.employee'].search([('guard_id','=',self.id)])
		self.replacement_count = self.env['sos.guard.shortfall'].search_count([('employee_id', '=', employee.id)])

	@api.multi
	@api.depends('attendance_ids')
	def _attendance_count(self):
		for rec in self:
			employee = self.env['hr.employee'].search([('guard_id','=',rec.id)])
			rec.attendance_count = self.env['sos.guard.attendance'].search_count([('employee_id', '=', employee.id),('slip_id', '=', False)])
		
	attendance_ids = fields.One2many('sos.guard.attendance', 'employee_id', 'Attendance History',domain="[('slip_id','=',False)]")
	#att_draft = fields.Boolean('Draft', compute='_check_draft_attendance',store=True)
	shortfall_count = fields.Integer('Shortfall', compute='_shortfall_count')
	replacement_count = fields.Integer('Replacement', compute='_replacement_count')
	attendance_count = fields.Integer('Attendance Count', compute='_attendance_count')
	

class sos_attendance_close(models.Model):
	_name ="sos.attendance.close"
	_inherit = ['mail.thread']
	_description ="Attendance Close"

	attendance_date = fields.Date('Attendance Date', required=True,track_visibility='onchange')
	attendance_mark_date = fields.Date('Attendance Mark Date', required=True,track_visibility='onchange')
	attendance_close_date = fields.Date('Attendance Close Date', required=True,track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',default='draft',track_visibility='onchange')
	
	@api.model
	def attendance_close_cron(self,nlimit=1):
		center_obj = self.env['sos.center']
		center_ids = center_obj.search([])
		today = str(datetime.today())[:10]
		att_close_ids = self.search([('state','=','draft'),('attendance_close_date','=',today)])
		if att_close_ids:
			for att_close_id in att_close_ids:
				att_close_id.state='done'
				m_date = datetime.strptime(att_close_id.attendance_date,'%Y-%m-%d').date()
				for center_id in center_ids:
					center_id.attendance_min_date = m_date + relativedelta(days=+1)
					center_id.attendance_max_date = m_date + relativedelta(days=+1)


## Attendance Testing Class ##
class sos_guard_attendance1(models.Model):
	_name = "sos.guard.attendance1"
	_inherit = ['mail.thread']
	_description = "Attendance"
	_order = 'id desc'
	
	#@api.one
	#@api.depends('name')
	#def get_duty_status(self):
	#	dt1 = fields.Date.today() + ' 09:15:00'
	#	dt2 = self.name
	#	
	#	if dt2:
	#		l2 = localDate(self, strToDatetime(dt2)).strftime("%Y-%m-%d %H:%M:%S")
	#		l1_date = fields.Datetime.from_string(dt1)
	#		l2_date = fields.Datetime.from_string(l2)
	#		duration = l2_date - l1_date
	#
	#		if duration:
	#			totsec = duration.total_seconds()
	#			h = totsec // 3600
	#			m = (totsec%3600) // 60
	#			self.late_time =  "%02dH:%02dM" %(h,m)
	#	
	#		if l2 <= dt1:
	#			self.duty_status = 'intime'
	#		else:
	#			self.duty_status = 'late'	
	
	name = fields.Datetime('Date', required=False,track_visibility='onchange')
	code = fields.Char('Code')
	device_datetime = fields.Datetime('Device Date', required=False,track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True,string = 'Project',track_visibility='onchange')
	center_id = fields.Many2one('sos.center','Center',track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', required=False,domain=[('active','=',True)], track_visibility='onchange')
	action = fields.Selection([('Normal', 'Normal'), ('in', 'In'), ('out', 'Out'), ('other','Other')], 'Action', track_visibility='onchange')
	current_action = fields.Selection([('present', 'Present'), ('absent', 'Absent'), ('leave', 'Leave'), ('double','Double'),('extra','Extra'),('extra_double','Extra Double')], 'Current Action', default='present', required=False, track_visibility='onchange')
	action_desc = fields.Many2one("sos.guard.action.reason", "Action Reason", help='Specifie the reason.')
	employee_id = fields.Many2one('hr.employee', "Employee", track_visibility='onchange')             
	state = fields.Selection([('draft','Draft'),('verify','Verify'),('counted','Counted'),('done','Done')],'Status',default='draft',track_visibility='onchange')
	slip_id = fields.Many2one('guards.payslip', "Pay Slip")
	device_id = fields.Many2one('sos.attendance.device','Device',track_visibility='onchange')
	month_att = fields.Boolean("Month att")
	department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
	duty_status = fields.Selection([('intime', 'In Time'), ('late', 'Late')], string = 'Duty Status', copy=False)
	late_time = fields.Char("Late Time")
	absent_reason = fields.Selection([('leave', 'Leave'),('short_leave', 'Short Leave'),('half_day_leave', 'Half Day Leave')], string = 'Absent Reason')							
	present_reason = fields.Selection([('on_field', 'Field'), ('out_station', 'Out Station'), ('visit', ' Visit/Official Duty')], string = 'Present Reason')							
	remarks = fields.Char('Remarks')
	staff_slip_id = fields.Many2one('hr.payslip','Staff Pay Slip')
	source = fields.Selection([('auto', 'Auto'), ('manual', 'Manual')], string='Source')
	
	
	@api.model
	def create(self, vals):
		code = vals.get('code',False)
		device_code = vals.get('device_id',False)
		employee_id = False
		device_id = False
		source = ''

		if device_code and not vals.get('employee_id', False):
			device_id = self.env['sos.attendance.device'].sudo().search([('device_number', '=', device_code)])
			source = 'auto'
		if device_code and vals.get('employee_id', False):
			device_id = self.env['sos.attendance.device'].sudo().search([('id', '=', vals.get('device_id'))])
			source = 'manual'

		if code:
			employee_id = self.env['hr.employee'].search([('code','=',code)])
		#if it is manual Attendance not pushed by the device
		if not code and vals.get('employee_id',False):
			employee_id = self.env['hr.employee'].search([('id','=',vals.get('employee_id'))])

		if not device_id and employee_id.current_post_id:
			device_id = self.env['sos.attendance.device'].search([('post_id','=',employee_id.current_post_id.id)])
			
		if employee_id:
			# if record already exist...then
			rec_exist = self.env['sos.guard.attendance1'].search([('name', '=', vals.get('name')), ('employee_id', '=', employee_id.id),('action', '=', vals.get('action'))])
			if rec_exist:
				raise UserError('Employee Record Already Exists, please check it.')

			#For Double Duty
			second_shift = str(fields.Date.today()) + ' 20:00:00'
			n1 = localDate(self, strToDatetime(vals['name'])).strftime("%Y-%m-%d %H:%M:%S")
		
			att_id = self.env['sos.guard.attendance1'].search([('employee_id','=',employee_id.id),('action','in',['Normal','in']),('name','<=',vals['name'])], order='id desc', limit=1)
			if att_id and second_shift <= n1:
				att_id.current_action = 'double'
				result =att_id
		
			#Create new Record
			else:
				vals['employee_id'] = employee_id.id
				vals['device_id'] = device_id and device_id.id or False
				vals['project_id'] = employee_id.project_id and employee_id.project_id.id or False
				vals['center_id'] = employee_id.center_id and employee_id.center_id.id or False
				vals['post_id'] = employee_id.current_post_id and employee_id.current_post_id.id or False
				vals['department_id'] = employee_id.department_id and employee_id.department_id.id or False
				vals['action'] = vals.get('action','in')
				vals['current_action'] = 'present'
				vals['source'] = source
				
				##if Guards then shift starts from 7:00 a.m
				if employee_id.department_id.id == 29: 
					dt1 = fields.Date.today() + ' 07:15:00'
				
				#if Staff then shift starts from 9:00 a.m
				else:
					dt1 = str(fields.Date.today()) + ' 09:15:00'
			
				dt2 = vals['name'] or False
				if dt2:
					l2 = localDate(self, strToDatetime(dt2)).strftime("%Y-%m-%d %H:%M:%S")
					l1_date = fields.Datetime.from_string(dt1)
					l2_date = fields.Datetime.from_string(l2)
					duration = l2_date - l1_date

					if duration:
						totsec = duration.total_seconds()
						h = totsec // 3600
						m = (totsec%3600) // 60
						vals['late_time'] =  "%02dH:%02dM" %(h,m)
	
					if l2 <= dt1:
						vals['duty_status'] = 'intime'
					else:
						vals['duty_status'] = 'late'
				result = super(sos_guard_attendance1, self).create(vals)
		else:
			raise UserError('Employee or Device record is not found in the System please check it.')
		return result

	@api.multi
	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise UserError(('You can not delete the Verified Records.'))	
			else:
				res = super(sos_guard_attendance1, rec).unlink()
			return res

	@api.onchange('employee_id')
	def onchange_employee(self):
		self.project_id = self.employee_id.project_id and self.employee_id.project_id.id or False
		self.center_id = self.employee_id.center_id and self.employee_id.center_id.id or False
		self.post_id = self.employee_id.current_post_id and self.employee_id.current_post_id.id or False
		self.department_id = self.employee_id.department_id and self.employee_id.department_id.id or False
		if self.employee_id.current_post_id:
			device_id = False
			device_id = self.env['sos.attendance.device'].search([('post_id','=',self.employee_id.current_post_id.id)])
			if device_id:
				self.device_id = device_id.id
	
	@api.onchange('device_id')
	def onchange_device(self):
		self.project_id = self.device_id.project_id and self.device_id.project_id.id or False
		self.center_id = self.device_id.center_id and self.device_id.center_id.id or False
		self.post_id = self.device_id.post_id and self.device_id.post_id.id or False


	@api.multi
	def action_verify(self):
		for rec in self:
			rec.state = 'verify'	

	@api.model
	def get_late_time(self, nlimit=100):
		recs = self.search([('name', '>=', fields.Date.today())])
		if recs:
			for rec in recs:
				dt1 = fields.Date.today() + ' 09:15:00'
				dt2 = rec.name
				
				if dt2:
					l2 = localDate(rec, strToDatetime(dt2)).strftime("%Y-%m-%d %H:%M:%S")
					l1_date = fields.Datetime.from_string(dt1)
					l2_date = fields.Datetime.from_string(l2)
					duration = l2_date - l1_date
	
					if duration and rec.current_action not in ('short_leave','half_day_leave', 'leave'):
						totsec = duration.total_seconds()
						if totsec > 0:
							late_mint = 0
							h = totsec // 3600
							m = (totsec%3600) // 60
							rec.late_time =  "%02dH:%02dM" %(h,m)
							late_mint = (h * 60) + m
							
							
							## Calculate the Month Last Day.
							loc_date = fields.Datetime.from_string(fields.Date.today())
							loc_month = loc_date + relativedelta(day=1, months=+1, days=-1)
							last_day =loc_month.day
							
							##Calculate The Wage Per Day, Hour and Mint. 
							contract = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id),('state','!=', 'done')], order='id', limit=1)
							
							if contract:
								wage = contract.wage or 0
								hours = last_day * 8
								mintues = hours * 60
								salary_per_day = wage / last_day
								salary_per_hour = wage / hours
								salary_per_mint = wage / mintues
								
								#Check If already record created for today.
								fine = self.env['hr.salary.inputs'].search([('employee_id','=',rec.employee_id.id),('date','=',fields.Date.today()),('name','=','FINE')])
								
								##Creating Records in Arrears for Fine.
								if late_mint > 0 and late_mint <=15:
									rec.remarks = 'Your Half Hour Salary will be deduct of Date: ' + fields.Date.today()
									amt = (salary_per_mint * 30)
									if not fine: 
										vals = {
											'employee_id': rec.employee_id and rec.employee_id.id,
											'center_id' : rec.center_id and rec.center_id.id,
											'name' : 'FINE',
											'date' : fields.Date.today(),
											'amount' : amt or 0,
											'state' : 'confirm',
											'description' : rec.remarks, 
										}
										#self.env['hr.salary.inputs'].sudo().create(vals) #remarked on the request of the Zahid
									
								if late_mint > 15 and late_mint <=30:
									rec.remarks = 'Your One Hour Salary will be deduct of Date: ' + fields.Date.today()
									amt = salary_per_hour
									if not fine:
										vals = {
											'employee_id': rec.employee_id and rec.employee_id.id,
											'center_id' : rec.center_id and rec.center_id.id,
											'name' : 'FINE',
											'date' : fields.Date.today(),
											'amount' : amt or 0,
											'state' : 'confirm',
											'description' : rec.remarks, 
										}
										#self.env['hr.salary.inputs'].sudo().create(vals) #remarked n the Request of the Zahid
									
								if late_mint > 30:
									rec.remarks = 'Your Half Day Salary (4 Hours) will be deduct of Date: ' + fields.Date.today()
									amt = (salary_per_hour * 4)
									if not fine:
										vals = {
											'employee_id': rec.employee_id and rec.employee_id.id,
											'center_id' : rec.center_id and rec.center_id.id,
											'name' : 'FINE',
											'date' : fields.Date.today(),
											'amount' : amt or 0,
											'state' : 'confirm',
											'description' : rec.remarks, 
										}
										#self.env['hr.salary.inputs'].sudo().create(vals) ##Remarked on the request of the Zahid
							
							## if employee Contract is not entered.
							if not contract:
								rec.remarks = 'This Employee Contract is not Entered, For Deduction it Required.'		
								
					if l2 <= dt1:
						rec.duty_status = 'intime'
					else:
						rec.duty_status = 'late'

			
class SOSPssAttendance(models.Model):
	_name = "sos.pss.attendance"
	_inherit = ['mail.thread']
	_description = "PSS Attendance"
	_order = 'id desc'
	
	name = fields.Datetime('Date', required=False,track_visibility='onchange')
	device_datetime = fields.Datetime('Device Date', required=False,track_visibility='onchange')
	device_id = fields.Many2one('sos.attendance.device','Device',track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee', "Employee", track_visibility='onchange')
	pss_id = fields.Many2one('sos.pss', string = 'PSS', track_visibility='onchange')
	center_id = fields.Many2one('sos.center', related='pss_id.center_id', string = 'Center', store=True, track_visibility='onchange')
	
	branch_status = fields.Boolean('Branch Status' ,default=True)
	atm_status = fields.Boolean('ATM Status', default=True)
	atm_light_camera = fields.Boolean('ATM Light & Camera', default=True)
	cor_light_camera = fields.Boolean('Cor.out Light & Camera', default=True)
	br_indoor_light = fields.Boolean('Br.indoor Light', default=True)
	gen_status = fields.Boolean('Gen & Other Access Status', default=True)
	skimming_device = fields.Boolean('Skimming Device at ATM', default=True)
	remarks = fields.Char('Remarks')
	type = fields.Char('Type')
	image_url = fields.Char('ImageURL')
	location_url = fields.Char('LocationURL')
	
	@api.model
	def center_assign_cron(self,nlimit=100):
		atts = self.env['sos.pss.attendance'].search([('center_id','=', False)])
		if atts:
			for att in atts:
				att.center_id = att.pss_id.center_id and att.pss_id.center_id.id or False
