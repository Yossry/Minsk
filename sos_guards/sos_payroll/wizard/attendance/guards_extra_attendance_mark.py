import time
import pdb
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class guards_extra_attendance_mark(models.TransientModel):
	_name = 'guards.extra.attendance.mark'
	_description = 'Guards Extra Attendance Mark'

	name = fields.Date('Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	line_ids = fields.One2many('guards.extra.attendance.mark.line', 'extra_att_id', 'Lines')

	@api.multi	
	def mark_attendance(self):
		att_pool = self.env['sos.guard.attendance']
		duty_pool = self.env['sos.guard.post']
		
		multan =  self.env['sos.center'].sudo().search([('id','=',19)])
		rec_date_min = multan.attendance_min_date
		rec_date_max = multan.attendance_max_date		

		for data in self:		
			name = data.name
			if name < rec_date_min:
				raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.')
			if name > rec_date_max:
				raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.')
			
			for line in data.line_ids:
				extra_count = 0
				#take post strength
				strength = line.post_id.guards or 0
				# Guard Post strength and Attendance Check
				self.env.cr.execute("SELECT sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total \
										FROM sos_guard_attendance t where t.post_id =%s and t.name = %s ",(line.post_id.id, name))
				attendance = self.env.cr.dictfetchall()[0]['total']
				if attendance is None:
					attendance = 0
					
				additional_guards = self.env['sos.additional.guard.proforma'].search([('post_id','=',line.post_id.id),('date_from','<=',name),('date_to','>=',name),('state','=','done'),('status','=','deployment'),('deployment_category','=','temporary')])
				if additional_guards:
					strength += sum(add_guard.guards for add_guard in additional_guards)
					
				if attendance < strength:
					#***** Extra Attendance Check *****#
					#***** there should be one regular (present) and one Extra Attendance *****#
					regular_att = self.env['sos.guard.attendance'].search([('name','=',name),('action','=','present'),('employee_id','=',line.employee_id.id)])
					extra_att = self.env['sos.guard.attendance'].search([('name','=',name),('action','=','extra'),('employee_id','=',line.employee_id.id)])
					extra_count = self.env['sos.guard.attendance'].search_count([('name','=',name),('action','=','extra'),('employee_id','=',line.employee_id.id)])
					
					if not extra_att or not regular_att and extra_count < 2:
						#Appointment Date Check
						if line.employee_id.appointmentdate <= name:
							#Center Check
							if name >= line.post_id.center_id.attendance_min_date and name <= line.post_id.center_id.attendance_max_date:
								#Project Check
								if name >= line.post_id.project_id.attendance_min_date and name <= line.post_id.project_id.attendance_max_date:
									#Post Check
									if name >= line.post_id.attendance_min_date and name <= line.post_id.attendance_max_date:			
										post_id = line.post_id.id
										project_id = line.post_id.project_id.id
										center_id = line.post_id.center_id.id
										employee_id = line.employee_id.id			
										guard_id = line.employee_id.guard_id.id
										aaction = line.action

										flag = True
										if aaction == 'double':
											att_id = att_pool.search([('name','=',name),('action','=','present'),('employee_id','=',employee_id)])
											if att_id:
												att_id.action = 'double'
												flag = False
										if flag:				
											rec_id = att_pool.create({
												'project_id': project_id,
												'post_id': post_id,
												'center_id': center_id,
												'name': name,
												'employee_id': employee_id,
												'action': aaction,
												'state': 'draft',
												'shift' : 'morning',
											})
									#Post Check End	
									else:
										raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.(Posts)')	
								# Project Check End	
								else:
									raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.(Projects)')	
							# Center Check End	
							else:
								raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.(Centers)')
						#Appointment Check End
						else:
							raise UserError(('Appointment Date of the Guard is (%s) which is Greater then the Attendance Marking Date (%s). This Action is Not Allowed.') %(line.employee_id.appointmentdate,name,))
					#Exta Attendance Check End
					else:
						raise UserError((""" Extra Attendance of this Guard is already marked for Specified date.\n
										Only One Regular And One Extra is allowed. \n
										If Regular Attendance (present) is not marked then Two Extra Attendance can be Marked"""))
				#Guard Post Strength
				else:
					raise ValidationError('Attendance Marked on this post Exceeded then the Post Guard Strengt. Contact to Mr.Zahid')		
		return {'type': 'ir.actions.act_window_close'}

class guards_extra_attendance_mark_line(models.TransientModel):
	_name = 'guards.extra.attendance.mark.line'
	_description = 'Guards Extra Attendance Mark Line'

	action = fields.Selection([('double','Double'), ('extra','Extra')], 'Action',default='extra',required=True)
	project_id = fields.Many2one('sos.project', string = 'Project')
	center_id = fields.Many2one('sos.center','Center')
	post_id = fields.Many2one('sos.post', string = 'Post',required=True)
	employee_id = fields.Many2one('hr.employee', "Guard",required=True,domain=[('current','=',True),('is_guard','=',True)])
	extra_att_id = fields.Many2one('guards.extra.attendance.mark')

	@api.onchange('post_id')	
	def onchange_post_id(self):		
		self.project_id = self.post_id.project_id.id
		self.center_id = self.post_id.center_id.id
		
		
