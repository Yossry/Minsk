import pdb
import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import math
import itertools
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError


class Holidays(models.Model):
	_inherit = 'hr.leave'
	
	state = fields.Selection([('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), 
		('validate', 'Approved')], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft', 
		help="The status is set to 'To Submit', when a holiday request is created.\nThe status is 'To Approve', when holiday request is confirmed by user." + 
			"\nThe status is 'Refused', when holiday request is refused by manager.\nThe status is 'Approved', when holiday request is approved by manager.")
	date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
		states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
	date_to = fields.Date('End Date', readonly=True, copy=False,
		states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')

	@api.onchange('date_from')
	def _onchange_date_from(self):
		""" If there are no date set for date_to, automatically set one 8 hours later than
			the date_from. Also update the number_of_days.
		"""
		date_from = self.date_from
		date_to = self.date_to

		# No date_to set so far: automatically compute one 8 hours later
		if date_from and not date_to:
			date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(days=1)
			self.date_to = str(date_to_with_delta)

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
		else:
			self.number_of_days_temp = 0
	
	def _get_number_of_days(self, date_from, date_to, employee_id):
		""" Returns a float equals to the timedelta between two dates given as string."""
		from_dt = fields.Datetime.from_string(date_from)
		to_dt = fields.Datetime.from_string(date_to)

		#if employee_id:
		#	employee = self.env['hr.employee'].browse(employee_id)
		#	return employee.get_work_days_count(from_dt, to_dt)

		time_delta = (to_dt - from_dt)
		
		#return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
		return math.ceil(time_delta.days + 1)

	@api.multi
	def action_confirm(self):
		super(Holidays, self).action_confirm()
		for holiday in self:			
			if self.number_of_days >= 0:
				raise UserError(_('Warning!\nNumber of Leave days are not valid.'))

	@api.multi
	def action_approve(self):
		for holiday in self:
			holiday.state='confirm'
