from odoo import tools
from odoo import models, fields, api, _

from odoo.exceptions import Warning, RedirectWarning, UserError
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from pytz import timezone, utc
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import pdb


def strToDate(strdate):
    return datetime.strptime(strdate, '%Y-%m-%d').date()


def strToDatetime(strdatetime):
    return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')


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


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _merge_kw(self, kw, kw_ext):
        new_kw = dict(kw, **kw_ext)
        # new_kw.update(
        #	attendances=kw.get('attendances', self.env['resource.calendar.attendance']) | kw_ext.get('attendances', self.env['resource.calendar.attendance']),
        #	leaves=kw.get('leaves', self.env['resource.calendar.leaves']) | kw_ext.get('leaves', self.env['resource.calendar.leaves'])
        # )
        return new_kw

    def _interval_new(self, start_datetime, end_datetime, kw=None):
        kw = kw if kw is not None else dict()
        # kw.setdefault('attendances', self.env['resource.calendar.attendance'])
        # kw.setdefault('leaves', self.env['resource.calendar.leaves'])
        return self._interval_obj(start_datetime, end_datetime, kw)

    @api.multi
    def get_work_hours_count(self, start_dt, end_dt, compute_leaves=True, domain=None):
        #Set timezone in UTC if no timezone is explicitly given
		#SARFRAZ DUE TO ERROR IN EMPLOYEE PROFILE
        #if not start_dt.tzinfo:
            #start_dt = start_dt.replace(tzinfo=utc)
        #if not end_dt.tzinfo:
            #end_dt = end_dt.replace(tzinfo=utc)
        #if compute_leaves:
         #   intervals = self._work_intervals(start_dt, end_dt, domain=domain)
        #else:
        #    intervals = self._attendance_intervals(start_dt, end_dt)
        #return sum(
        #    (stop - start).total_seconds() / 3600
        #    for start, stop, meta in intervals
        #)
        return 0


class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    state = fields.Selection(
        (('draft', 'Unverified'), ('verified', 'Verified'), ('locked', 'Locked'), ('unlocked', 'Un-Locked')), 'State',
        default='draft', required=True, readonly=True)
    in_att_method = fields.Char('In Method')
    out_att_method = fields.Char('Out Method')

    check_in = fields.Datetime(string="Check In", default=False, required=False)
    in_date = fields.Char(compute='_compute_date', store=True)
    out_date = fields.Char(compute='_compute_date', store=True)
    in_time = fields.Char(compute='_compute_date', store=True)
    out_time = fields.Char(compute='_compute_date', store=True)
    worked_hours_time = fields.Char('Worked Hours Time', compute='_compute_worked_hours', store=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True)

    @api.multi
    @api.depends('check_in', 'check_out')
    def _compute_date(self):
        for att in self:
            if att.check_in:
                check_in = localDate(self, strToDatetime(att.check_in))
                att.in_date = check_in.strftime("%d-%m-%Y")
                att.in_time = check_in.strftime("%H:%M:%S")
            if att.check_out:
                check_out = localDate(self, strToDatetime(att.check_out))
                att.out_date = check_out.strftime("%d-%m-%Y")
                att.out_time = check_out.strftime("%H:%M:%S")

    #	@api.model_cr
    #	def init(self):
    #		tools.drop_view_if_exists(self.env.cr, 'hr_attendance_report_employee_present')
    #		self.env.cr.execute("""CREATE or REPLACE VIEW hr_attendance_report_employee_present as (
    #				select * from crosstab(
    #				'select employee_id, extract(month from check_in) as month, count(distinct to_char(check_in,''%YYYY-%MM-%DD''))
    #					from hr_attendance where check_in >= ''2018-01-01'' or check_out >= ''2018-01-01'' group by 1,2 order by employee_id,month',
    #				'select m from generate_series(1,12) m'
    #			) as (employee int,jan float,feb float,mar float,apr float,may float,jun float,jul float,aug float,sep float,oct float,nov float,dec float)
    #		)""")

    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out and attendance.check_in:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                            fields.Datetime.from_string(
                                                                                                attendance.check_in))),
                }))
            elif attendance.check_out and not attendance.check_in:
                result.append((attendance.id, _("%(empl_name)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                            fields.Datetime.from_string(
                                                                                                attendance.check_in))),
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
        return result

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = delta.total_seconds() / 3600.0

                totsec = delta.total_seconds()
                h = totsec // 3600
                m = (totsec % 3600) // 60
                attendance.worked_hours_time = "%02d:%02d" % (h, m)

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        pass

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee."""
        pass

    @api.model
    def create(self, vals):
        if vals.get('check_in', False) and self.is_locked(vals['employee_id'], vals['check_in']):
            emp_data = self.env['hr.employee'].browse(vals['employee_id'])
            raise UserError(_("You may not add an attendance record to a locked period.\nEmployee: %s\nTime: %s") % (
            emp_data.name, vals['check_in']))
        obj = super(hr_attendance, self).create(vals)
        attendances = [(obj.employee_id, obj.check_in and obj.check_in[:10] or obj.check_out[:10])]
        return obj

    @api.multi
    def unlink(self):
        for punch in self:
            if punch.state in ['verified', 'locked']:
                raise UserError(_("""You may not delete a record that is in a %s state:\n
					Employee: %s, Checkin: %s, Checkout: %s""") % (
                punch.state, punch.employee_id.name, punch.check_in, punch.check_out))
        res = super(hr_attendance, self).unlink()

    @api.one
    def write(self, vals):
        if (self.state in ['verified', 'locked'] and (vals.get('employee_id'))):
            raise UserError(_("""You may not write to a record that is in a %s state:\n
				Employee: %s, Checkin: %s, Checkout: %s""") % (
            self.state, self.employee_id.name, self.check_in, self.check_out))
        res = super(hr_attendance, self).write(vals)
        return res


class res_company(models.Model):
    _inherit = 'res.company'

    attendance_policy = fields.Selection([('none','No Attendance'),('daily','Daily Attendance'),('monthly','Monthly Attendance'),
                                          ('overtime','Overtime'),('bio_month','Bio Device with Monthly Counting')], 'Attendance Policy' , default='monthly')
