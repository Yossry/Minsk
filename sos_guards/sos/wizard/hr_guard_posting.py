# -*- coding: utf-8 -*-
import pdb
import time
from datetime import datetime
from odoo import tools
from odoo import api, fields, models, _
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()


class hr_guard_terminate(models.TransientModel):
	_name ='hr.guard.terminate'
	_description = 'Guards Termination from Current Post'
			
	employee_id = fields.Many2one('hr.employee', string = 'Guard')
	todate = fields.Date('To Date',required=True)
	lbl =  fields.Char('Labl', size=256)
	remarks = fields.Char('Remarks', size=64)
	to_reason = fields.Selection([('terminate','Terminate'),('escape','Escaped')],'Reason',help='Select the Reason of Termination',required=True)
	
	@api.model	
	def default_get(self,vals):
		ret = super(hr_guard_terminate,self).default_get(vals)
		employee = self.env['hr.employee'].browse(self._context.get('active_id',False))
		current_post = employee.current_post_id and employee.current_post_id.name or False
		if current_post:
			msg = 'This wizard will Terminate the ' + employee.name + ' from Current Post ' + employee.current_post_id.name
			ret['employee_id'] = employee.id
			ret['lbl'] = msg
		return ret

	@api.multi	
	def guard_terminate(self):
		employee_pool = self.env['hr.employee']
		duty_pool = self.env['sos.guard.post']
		log_obj = self.env['sos.account.info.log']
		exit_obj = self.env['sos.guards.exit.form']
				
		for data in self:
			if data.employee_id.appointmentdate < data.todate:
				first_day = str(datetime.now() + relativedelta.relativedelta(day=1))[:10]
				last_day = str(datetime.now() + relativedelta.relativedelta(day=31))[:10]
				
				#Terminate Within the given Month
				if (data.todate >= strToDate(first_day)) and (data.todate <= strToDate(last_day)):
					#guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], limit=1, order='fromdate desc')			
					guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], order='fromdate desc')
					for guard_post_id in guard_post_ids:
						if guard_post_id.fromdate < data.todate:
							UserError('Are You Mad?') 						
						guard_post_id.write({
							'todate' : data.todate,
							'to_reason' : data.to_reason,
							'current' : False,
							'remarks' : data.remarks or False,
						})
					
						## Entry in Account info Log ##
						vals = {
							'name' : data.employee_id.name,
							'employee_id' : data.employee_id.id, 
							'code' : data.employee_id.code,
							'resigdate' : data.todate,
							'date' : data.todate,
							'bank_id' : data.employee_id.bank_id and data.employee_id.bank_id.id,
							'bankacctitle' : data.employee_id.bankacctitle or '',
							'bankacc' : data.employee_id.bankacc or '',
							'accowner' : data.employee_id.accowner or '',
							'branch' : data.employee_id.branch or '',
							'acc_creation_date' : data.employee_id.acc_creation_date or data.employee_id.appointmentdate
							}
								
						#log_obj.suspend_security().create(vals)
						log_obj.create(vals)
					
						## Vals For Entry in Exit Form ##
						exit_vals = {
							'employee_id' : data.employee_id.id,
							'project_id' : data.employee_id.project_id.id,
							'center_id' : data.employee_id.center_id.id,
							'post_id' : data.employee_id.current_post_id.id,   
							'code' : data.employee_id.code,
							'cnic0' : data.employee_id.cnic,
							'appointment_date' : data.employee_id.appointmentdate,
							'date' : data.todate,
							'bank_id' : data.employee_id.bank_id and data.employee_id.bank_id.id or False,
							'bankacctitle' : data.employee_id.bankacctitle or '',
							'bankacc' : data.employee_id.bankacc or '',
							'accowner' : data.employee_id.accowner or '',
							'salary' : True,
							'security' : True,
							}
						#exit_obj.suspend_security().create(exit_vals)
						data.employee_id.write({'resigdate': data.todate, 'bank_id': False ,'bankacctitle': ' ', 'bankacc': ' ', 'accowner' : 'other', 'branch' : ' '})
				else:
					
					raise UserError(('You Can Terminate the Guard Within the Current Month Previous Termination are Not Allowed. While You are Terminating on (%s) and you can Terminate in between (%s) and (%s)') %(data.todate,first_day,last_day,))			
			else:
				raise UserError(('Appointment Date of the Guard is (%s) which is Greater then the Selected Date (%s) To Terminate. This Action is Not Allowed.') %(data.employee_id.appointmentdate,data.todate,))		
							
		return {'type': 'ir.actions.act_window_close'}


class hr_guard_transfer(models.TransientModel):
	_name ='hr.guard.posting'
	_description = 'Guards Posting at Required Posts'
			
	project_id =fields.Many2one('sos.project', string = 'Project',required=True)
	post_id = fields.Many2one('sos.post', string = 'Post',required=True)	
	employee_id = fields.Many2one('hr.employee', string = 'Guard')
	center_id = fields.Many2one('sos.center', string = 'Center')	

	fromdate = fields.Date('Posting Date',required=True)
	todate = fields.Date('Transfer Date')
	
	lbl =  fields.Char('Labl', size=256)
	remarks = fields.Char('Remarks', size=64)
	current = fields.Boolean('Current Post')
		
	@api.model	
	def default_get(self,fields):
		ret = super(hr_guard_transfer,self).default_get(fields)		
		context = dict(self._context or {})
		employee_id = context.get('active_id',False)
		employee = self.env['hr.employee'].browse(employee_id)
		current_post = employee.current_post_id and employee.current_post_id.name or False
		current = employee.current or False
		
		if employee_id:
			msg = 'This wizard will '
			if employee.current:
				msg = msg + 'Transfer the ' + employee.name + ' at the new Post. His Current post is '
				if current_post:
					msg = msg + employee.current_post_id.name
				
			else:	
				msg = msg + 'Post the ' + employee.name + ' at the required Post.'			
			ret['employee_id'] = employee_id
			ret['current'] = employee.current
			ret['center_id'] = employee.center_id.id			
			ret['lbl'] = msg
		return ret

	@api.multi	
	def post_transfer(self):
		
		context = dict(self._context or {})
		employee_pool = self.env['hr.employee']
		duty_pool = self.env['sos.guard.post']
		
		for data in self:
			to_date = False
			
			## Checking appointment date ##
			## User cannot Appoint the Guard on the Post Before the Appointment Date of Guard ## 
			if data.employee_id.appointmentdate <= data.fromdate:
				if data.current:
					if data.todate > data.fromdate:
						raise UserError(_('Have you any Sense?'))
					#guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], limit=1, order='fromdate desc')
					guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], order='fromdate desc')
					
					for guard_post_id in guard_post_ids:
						if guard_post_id.fromdate > data.todate:
							raise UserError(_('Are You Mad?')) 						
	
						guard_post_id.write({
							'todate': data.todate,
							'to_reason': 'transfer',
							'current': False,
							'remarks': data.remarks or False,
						})
						
				## Checking Whether any Duty Post Active Before Appointing ##
				duty_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], order='fromdate desc')
				if duty_ids:
					raise UserError(('This Guard Is Already Appointment On Another Post. First Terminate It From That Post.'))
				else:
					## Creating Entry in the sos_guard_post ##	
					rec_id = duty_pool.sudo().create({
						'project_id': data.project_id.id,
						'post_id': data.post_id.id,
						'current': True,
						'employee_id': data.employee_id.id,
						'guard_id': data.employee_id.guard_id.id,
						'fromdate': data.fromdate,
						'todate': False
					})
					data.employee_id.guard_id.write({'resigdate': False})
			
			else:
				raise UserError(('Appointment Date of the Guard is (%s) which is Greater then the Posting Date (%s). This Action is Not Allowed.') %(data.employee_id.appointmentdate,data.fromdate,))	
				
		return {'type': 'ir.actions.act_window_close'}
	
class hr_post_guard_transfer(models.TransientModel):

	_name ='hr.post.guard.transfer'
	_description = 'Guards Posting at Required Posts'
			
	center_id = fields.Many2one('sos.center','Center')
	employee_id = fields.Many2one('hr.employee', string = 'Guard',required=True)
	project_id = fields.Many2one('sos.project', string = 'Project',required=True)
	post_id = fields.Many2one('sos.post', string = 'Post',required=True)		
	fromdate = fields.Date('Posting Date',required=True)
	todate = fields.Date('Transfer Date')
	lbl = fields.Char('Labl', size=256)
	remarks = fields.Char('Remarks', size=64)
	current = fields.Boolean('Current Post')

	current1 = fields.Boolean('Current1')

	
	@api.model	
	def default_get(self,fields):
		ret = super(hr_post_guard_transfer,self).default_get(fields)		
		context = dict(self._context or {})
		post_id = context.get('active_id',False)
		post = self.env['sos.post'].browse(post_id)
	
		current_post = employee.current_post_id and employee.current_post_id.name or False
		current = employee.current or False

		if post_id:
			msg = 'This wizard will Transfer/Post the employees from ' + post.name + ' at the required Post.'					
			ret['post_id'] = post_id
			ret['project_id'] = post.project_id.id
			ret['center_id'] = post.center_id.id			
			ret['lbl'] = msg
		return ret

	@api.onchange('employee_id')	
	def onchange_guard_id(self):
		current = False
		current1 = False
		if employee_id:
			
			guard_post_ids = self.env['sos.guard.post'].search([('employee_id', '=', employee_id)], limit=1, order='fromdate desc')
			for guard_post_id in guard_post_ids:
				current1 = guard_post_id.current
				if guard_post_id.current and guard_post_id.post_id.id == self.post_id.id:
					current = True
				
		self.current = current
		self.current1 = current1	


	@api.multi	
	def post_transfer(self):
		
		context = dict(self._context or {})
		employee_pool = self.env['hr.employee']
		duty_pool = self.env['sos.guard.post']
		
		for data in self:
			to_date = False
			
			# # this code is diffrent from new one
			#if guard exit form is already entered in the system then do not reappoint 
			if data.employee_id.exit_form and data.employee_id.exit_form_id and not data.employee_id.exit_form_id.state == 'close':
				raise UserError(("""This Guard have the Exit Form in the System, which is not finalized (closed).\n 
								To Reappoint, please Process the Exit Form. \n 
								Possible Solutions Are:- \n 
								1- Delete the Exit Form. \n
								2- Complete the Steps to Close the Exit Form. \n 
								3- Contact your IT Department."""))
			
			else:
			# ///
				## Checking appointment date ##
				## User cannot Appoint the Guard on the Post Before the Appointment Date of Guard ## 
				if data.employee_id.appointmentdate <= data.fromdate:
					if data.current:
						if data.todate > data.fromdate:
							raise UserError(_('Have you any Sense?'))
						#guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], limit=1, order='fromdate desc')
						guard_post_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], order='fromdate desc')
					
						for guard_post_id in guard_post_ids:
							if guard_post_id.fromdate > data.todate:
								raise UserError(_('Are You Mad?')) 						
	
							guard_post_id.write({
								'todate': data.todate,
								'to_reason': 'transfer',
								'current': False,
								'remarks': data.remarks or False,
							})
						
					## Checking Whether any Duty Post Active Before Appointing ##
					duty_ids = duty_pool.search([('employee_id', '=', data.employee_id.id),('todate', '=', False)], order='fromdate desc')
					if duty_ids:
						raise UserError(('This Guard Is Already Appointment On Another Post. First Terminate It From That Post.'))
					else:
						## Creating Entry in the sos_guard_post ##	
						rec_id = duty_pool.suspend_security().create({
							'project_id': data.project_id.id,
							'post_id': data.post_id.id,
							'current': True,
							'employee_id': data.employee_id.id,
							'guard_id': data.employee_id.guard_id.id,
							'fromdate': data.fromdate,
							'todate': False
						})
						data.employee_id.guard_id.write({'resigdate': False,'exit_form':False})
						# # this code is diffrent from new one
						if data.employee_id.exit_form_id:
							data.employee_id.exit_form_id = False
			# ///
				else:
					raise UserError(('Appointment Date of the Guard is (%s) which is Greater then the Posting Date (%s). This Action is Not Allowed.') %(data.employee_id.appointmentdate,data.fromdate,))	
				
		return {'type': 'ir.actions.act_window_close'}
	

