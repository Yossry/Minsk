import time
import pdb
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from pytz import common_timezones


### Policy Group
class policy_groups(models.Model):
	_name = 'hr.policy.group'
	_description = 'HR Policy Groups'
	
	name = fields.Char('Name',size=128)
	contract_ids = fields.One2many('hr.contract','policy_group_id','Contracts')
	absence_policy_ids = fields.Many2many('hr.policy.absence', 'hr_policy_group_absence_rel','group_id', 'absence_id', 'Absence Policy')
	ot_policy_ids = fields.Many2many('hr.policy.ot', 'hr_policy_group_ot_rel','group_id', 'ot_id', 'Overtime Policy')

class policy_absence(models.Model):
	_name = 'hr.policy.absence'
	_description = 'HR Policy Absence'
	_order = 'date desc'

	name = fields.Char('Name', size=128, required=True)
	date = fields.Date('Effective Date', required=True)
	line_ids = fields.One2many('hr.policy.line.absence', 'policy_id', 'Policy Lines')

	def get_codes(self):
		res = []
		[res.append((line.code, line.name, line.type, line.rate, line.use_awol)) for line in self.line_ids]
		return res

	def paid_codes(self):
		res = []
		[res.append((line.code, line.name)) for line in self.line_ids if line.type == 'paid']
		return res

	def unpaid_codes(self):
		res = []
		[res.append((line.code, line.name)) for line in self.line_ids if line.type == 'unpaid']
		return res

class policy_line_absence(models.Model):
	_name = 'hr.policy.line.absence'
	_description = 'HR Absence Policy Detail'

	name = fields.Char('Name', size=64, required=True)
	code = fields.Char('Code', required=True, help="Use this code in the salary rules.")
	holiday_status_id = fields.Many2one('hr.leave.type', 'Leave', required=True)
	policy_id = fields.Many2one('hr.policy.absence', 'Policy')
	type = fields.Selection([('paid', 'Paid'),('unpaid', 'Unpaid'),('dock', 'Dock')],'Type',required=True, help="Determines how the absence will be treated in payroll. The 'Dock Salary' type will deduct money (useful for salaried employees).",)
	rate = fields.Float('Rate', required=True, help='Multiplier of employee wage.')
	use_awol = fields.Boolean('Absent Without Leave',help='Use this policy to record employee time absence not covered by other leaves.')
	
	def onchange_holiday(self, holiday_status_id):
		res = {'value': {'name': False, 'code': False}}
		if not holiday_status_id:
		    return res
		data = self.env['hr.leave.type'].browse(holiday_status_id)
		res['value']['name'] = data.name
		res['value']['code'] = data.code
		return res


class policy_ot(models.Model):
	_name = 'hr.policy.ot'
	_description = 'Overtime Policy'
	_order = 'date desc'

	name = fields.Char('Name', size=128, required=True)
	date = fields.Date('Effective Date', required=True)
	line_ids = fields.One2many('hr.policy.line.ot', 'policy_id', 'Policy Lines')
	

	def get_codes(self):
		res = []
		[res.append((line.code, line.name, line.type, line.rate)) for line in self.line_ids]
		return res

	def daily_codes(self):
		res = []
		[res.append((line.code, line.name)) for line in self.line_ids if line.type == 'daily']
		return res

	def restday_codes(self):
		return [(line.code, line.name) for line in self.line_ids if line.type == 'weekly' and line.active_after_units == 'day']

	def restday2_codes(self):
		res = []
		[res.append((line.code, line.name)) for line in self.line_ids if line.type == 'restday']
		return res

	def weekly_codes(self):
		return [(line.code, line.name) for line in self.line_ids if line.type == 'weekly' and line.active_after_units == 'min']

	def holiday_codes(self):
		return [(line.code, line.name) for line in self.line_ids if line.type == 'holiday']


class policy_line_ot(models.Model):
	_name = 'hr.policy.line.ot'
	_description = 'HR Overtime Policy Detail'

	def _tz_list(self):
		res = tuple()
		for name in common_timezones:
			res += ((name, name),)
		return res

	name = fields.Char('Name', size=64, required=True)
	policy_id = fields.Many2one('hr.policy.ot', 'Policy')
	type = fields.Selection([('daily', 'Daily'),('weekly', 'Weekly'),('restday', 'Rest Day'),('holiday', 'Public Holiday')],'Type', required=True)
	weekly_working_days = fields.Integer('Weekly Working Days')
	active_after = fields.Integer('Active After', help="Minutes after which this policy applies")
	active_start_time = fields.Char('Active Start Time', size=5, help="Time in 24 hour time format")
	active_end_time = fields.Char('Active End Time', size=5, help="Time in 24 hour time format")
	tz = fields.Selection(_tz_list, 'Time Zone')
	rate = fields.Float('Rate', required=True, help='Multiplier of employee wage.')
	code = fields.Char('Code', required=True, help="Use this code in the salary rules.")



