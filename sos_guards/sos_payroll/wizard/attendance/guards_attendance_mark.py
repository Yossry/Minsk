import time
import pdb
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class guards_attendance_mark(models.TransientModel):
	_name = 'guards.attendance.mark'
	_description = 'Guards Attendance Mark'
	
	name = fields.Date('Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', string = 'Project')
	center_id = fields.Many2one('sos.center','Center')
	post_id = fields.Many2one('sos.post', string = 'Post')
	lbl = fields.Char('Processed')
	
	@api.multi		
	def mark_attendance(self):
		
		att_pool = self.env['sos.guard.attendance']
		shortfall_pool = self.env['sos.guard.shortfall']
		replacement_pool = self.env['sos.guard.replacement']
		duty_pool = self.env['sos.guard.post']
			
		
		for data in self:		
			name = data.name 
		
			args = [('current','=',True)]	
			center_id = data.center_id and data.center_id.id or False
			if center_id:
				args.append(('post_id.center_id','=', center_id))
				
				center_rec = self.env['sos.center'].browse(center_id)
				rec_date_min = center_rec.attendance_min_date
				rec_date_max = center_rec.attendance_max_date
			else:
				center_rec = self.env['sos.center'].browse(19)
				rec_date_min = center_rec.attendance_min_date
				rec_date_max = center_rec.attendance_max_date
		
			if name < rec_date_min:
				raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.')
			
			if name > rec_date_max:
				raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.')
				
			project_id = data.project_id and data.project_id.id or False
			if project_id:
				args.append(('project_id','=', project_id))
			
			post_id = data.post_id and data.post_id.id or False
			if post_id:
				args.append(('post_id','=', post_id))	
		
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
					
				att_id = att_pool.search([('name','=',name),('action','=','present'),('employee_id','=',guard_duty.employee_id.id)])
				if not att_id:
					if guard_duty.employee_id.appointmentdate <= name:
						
						if 	name >= guard_duty.post_id.attendance_min_date and name <= guard_duty.post_id.attendance_max_date:
							if (guard_duty.project_id and guard_duty.post_id):
								vals = {
									'project_id': guard_duty.project_id.id,
									'post_id': guard_duty.post_id.id,
									'center_id': guard_duty.post_id.center_id.id,
									'name': name,
									'employee_id': guard_duty.employee_id.id,
									'action': att_action,
									'state': 'draft',
									'shift' : 'morning',
								}										
								rec_id = att_pool.create(vals)
								cnt = cnt + 1
						else:
							raise ValidationError('Attendance Mark of the Said Date has been blocked. Please Contact Head Office.(Posts)')
					
					else:
						raise UserError(('Appointment Date of the Guard is (%s) which is Greater then the Attendance Marking Date (%s). This Action is Not Allowed.') %(guard_duty.employee_id.appointmentdate,name,))
		return {'type': 'ir.actions.act_window_close'}


