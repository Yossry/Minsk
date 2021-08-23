import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SOSStaffTransferwizard(models.TransientModel):
	_name = 'sos.staff.transfer.wizard'
	_description = 'Staff Transfer Wizard'
	
	@api.model
	def _get_employee_id(self):
		emp_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
		if emp_id:
			return emp_id.id
		return True	
		
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=_get_employee_id)
	old_segment_id = fields.Many2one('hr.segmentation',related='employee_id.segment_id', string='Old Segment')
	old_sub_segment_id = fields.Many2one('hr.sub.segmentation',related='employee_id.sub_segment_id', string='Old Sub Segment')
	old_department_id = fields.Many2one('hr.department',related='employee_id.department_id', string='Old Department')		
	old_job_id = fields.Many2one('hr.job',string='Old Job',related='employee_id.job_id')
	old_parent_id = fields.Many2one('hr.employee',related='employee_id.parent_id',string=' Old Manager')
	old_coach_id = fields.Many2one('hr.employee',related='employee_id.coach_id',string='Old Coach')
	old_center_id = fields.Many2one('sos.center',related='employee_id.center_id',string='Old Center')
	
	new_segment_id = fields.Many2one('hr.segmentation', string='Segment')
	new_sub_segment_id = fields.Many2one('hr.sub.segmentation',string='Sub Segment')
	new_department_id = fields.Many2one('hr.department', string='Department')		
	new_job_id = fields.Many2one('hr.job',string='Job')
	new_parent_id = fields.Many2one('hr.employee',string='Manager')
	new_coach_id = fields.Many2one('hr.employee',string='Coach')
	new_center_id = fields.Many2one('sos.center',string='Center')

	@api.multi
	def sos_staff_transfer(self):
		self.ensure_one()
		if not self.employee_id.is_guard: 
			contract_id = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')], order='date_start', limit=1)	
			if contract_id:
				contract_id.department_id = self.new_department_id and self.new_department_id.id or self.old_department_id.id or False
				contract_id.job_id = self.new_job_id and self.new_job_id.id or self.old_job_id.id or False
			
			if self.new_job_id:
				self.env.cr.execute("update hr_employee set job_id=%s where id = %s",(self.new_job_id.id,self.employee_id.id))
				
			vals = {
				'segment_id' : (self.new_segment_id and self.new_segment_id.id)  or (self.old_segment_id and self.old_segment_id.id) or False,
				'sub_segment_id' : (self.new_sub_segment_id and self.new_sub_segment_id.id)  or (self.old_sub_segment_id and self.old_sub_segment_id.id) or False,
				'department_id' : (self.new_department_id and self.new_department_id.id)  or (self.old_department_id and self.old_department_id.id) or False,
				'parent_id' : (self.new_parent_id and self.new_parent_id.id) or (self.old_parent_id and self.old_parent_id.id) or False,
				'coach_id' : (self.new_coach_id and self.new_coach_id.id) or (self.old_coach_id and self.old_coach_id.id) or False,
				'center_id' : (self.new_center_id and self.new_center_id.id) or (self.old_center_id and self.old_center_id.id) or False,
				#'job_id' : self.new_job_id and self.new_job_id.id or self.old_job_id and self.old_job_id.id or False,
				}
					
			self.employee_id.sudo().write(vals)
			
			new_rec = self.env['hr.staff.transfer.history'].sudo().create(vals)
			if new_rec:
				new_rec.employee_id = self.employee_id and self.employee_id.id or False
				new_rec.job_id = (self.new_job_id and self.new_job_id.id) or (self.old_job_id and self.old_job_id.id) or False
				
		else:
			raise UserError(('This Action is not allowed for the Guards. Only for Staff.'))
		return {'type': 'ir.actions.act_window_close'}	 
	
