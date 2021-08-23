from odoo import api, fields, models, _
from odoo import tools
import pdb


class sos_attendance_device_report(models.Model):
	""" Attendance Analysis """
	_name = "sos.device.attendance.report"
	_auto = False
	_description = "Devices Attendance Analysis"
	_order = 'name desc'

	name = fields.Date('Date', readonly=True)
	post_id = fields.Many2one('sos.post', 'Post')
	guards = fields.Integer(string="Guards")
	attendance = fields.Integer(string="Attendance")
	shortfall = fields.Integer(string="Shortfall")

	def init(self, cr):
		tools.drop_view_if_exists(cr, 'sos_device_attendance_report')
		cr.execute("""
			CREATE OR REPLACE VIEW sos_device_attendance_report AS (
				select
					min(t.id) as id,
					date(t.name) as name,
					p.id as post_id,
					p.guards as guards,
					count(*) as attendance,
					p.guards - count(*) as shortfall
				from
					"sos_guard_attendance1" t
					
				join
					"sos_post" p
				 on
                    (t.post_id = p.id)	  	 
				WHERE
					(t.post_id = p.id)
				GROUP BY 
					(date(t.name),p.id,p.guards)		
			)""")
