import pdb
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime

class SOSAttendanceDevice(models.Model):
	_name = "sos.attendance.device"
	_inherit = ['mail.thread']
	_description = "Attendance Devices "


	name = fields.Char('Name')
	device_number = fields.Char('Device Number')
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=False, \
		states={'draft': [('readonly', False)]},track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=False, states={'draft': [('readonly', False)]}, \
		track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, track_visibility='onchange')
	city = fields.Char('City', required=False, track_visibility='onchange')
	conn_company = fields.Selection([('mobilink','Mobilink'),('warid','Warid'),('zong','Zong'),('ufone','Ufone'),('telenor','Telenor'),('other','Other')],'Connection', track_visibility='onchange')
	sim_no = fields.Char('Sim No.', track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',default='draft', track_visibility='onchange')
	device_status = fields.Selection([('post','Post'),('regional_office','Regional Office'),('regional_stock','Regional Stock'),('faulty','Faulty')],'Device Status', track_visibility='onchange')
	pss_id = fields.Many2one('sos.pss', string = 'PSS', index=True, required=False, track_visibility='onchange')
	remarks = fields.Text('Remarks')
	
	_sql_constraints = [
		('device_number_uniq', 'unique(device_number)', 'Duplicate entry of Device Number is not allowed!'),
	]
	
	@api.multi
	def device_done(self):
		for rec in self:
			rec.write({'state':'done'})

	@api.model
	def create(self, vals):
		if vals.get('post_id',False):
			post_rec = self.env['sos.post'].search([('id','=',vals['post_id'])])
			post_name = post_rec.name
			vals['name'] = post_name + '/Device/' + vals['device_number']
		elif vals.get('pss_id',False):
			pss_rec = self.env['sos.pss'].search([('id','=',vals['pss_id'])])
			pss_name = pss_rec.name
			vals['name'] = pss_name + '/Device/' + vals['device_number']
		result = super(SOSAttendanceDevice, self).create(vals)
		return result

	@api.multi
	def write(self, vals):
		if vals.get('post_id',False):
			post_rec = self.env['sos.post'].search([('id','=',vals['post_id'])])
			post_name = post_rec.name
			vals['name'] = post_name + '/Device/' + self.device_number
		elif vals.get('pss_id',False):
			pss_rec = self.env['sos.pss'].search([('id','=',vals['pss_id'])])
			pss_name = pss_rec.name
			vals['name'] = pss_name + '/Device/' + self.device_number
		result = super(SOSAttendanceDevice, self).write(vals)
		return result

	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise UserError('You can not delete a Device which are not in Draft State')
		ret = super(SOSAttendanceDevice, self).unlink()
		return ret


class SOSPSS(models.Model):
	_name = "sos.pss"
	_description = "PSS"
	_order = 'name desc'
	
	code = fields.Char('Code')
	name = fields.Char('Name')
	city = fields.Char('City')
	center_id = fields.Many2one('sos.center', string='Center')	
