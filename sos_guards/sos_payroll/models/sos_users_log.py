import pdb
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import itertools
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError


## Attendance Log Class ##
class sos_attendance_log(models.Model):
	_name = "sos.attendance.log"
	_description = "Attendance Logs"
	_inherit = ['mail.thread']
	_order = 'id desc'

	name = fields.Date('Attendance Date')
	date = fields.Date('Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	project_id = fields.Many2one('sos.project', required=True,string = 'Project')
	center_id = fields.Many2one('sos.center','Center')
	post_id = fields.Many2one('sos.post', string = 'Post', required=False)
	action = fields.Selection([('present', 'Present'), ('absent', 'Absent'), ('leave', 'Leave'), ('double','Double'),('extra','Extra'),('extra_double','Extra Double')], 'Action', required=True)
	employee_id = fields.Many2one('hr.employee', "Employee", domain=[('is_guard','=',True),('current','=',True)])             
	state = fields.Selection([('draft','Draft'),('counted','Counted'),('done','Done')],'Status')
	user_id = fields.Many2one('res.users', required=True, string = 'User Who Deleted Attendance')



			
					
		
		
	
