# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
CT = fields.Datetime.context_timestamp
from odoo.exceptions import UserError
import datetime
from datetime import timedelta, date
from pytz import timezone, all_timezones, UTC
import pytz
import time
import math


def period_datetime(a, b):
    dt_list = []
    nod = (b - a).days
    if a.date() == b.date():
        return [[a, b]]
    dt_list.append([a, a.replace(hour=23, minute=59, second=59, microsecond=999999)])
    for i in range(1 , nod):
        dt_list.append([a.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=i),
                    a.replace(hour=23, minute=59, second=59, microsecond=999999)+ datetime.timedelta(days=i)])
    dt_list.append([b.replace(hour=0, minute=0, second=0, microsecond=0), b])
    return dt_list


class resource_calendar(models.Model):
    _inherit = "resource.calendar"

    overtime_off_days = fields.Float('Holiday Overtime Rate')
    overtime_work_days = fields.Float('Normal Overtime Rate')


class hr_overtime(models.Model):
    _name = "hr.overtime"
    _rec_name = "employee_id"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    date = fields.Date('Date', required=True, readonly=True, default=fields.Date.today(), states={'draft': [('readonly', False)]}, track_visibility='onchange')
    # start_datetime = fields.Datetime('Start Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    # end_datetime = fields.Datetime('End Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    start_date = fields.Date('Start Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    end_date = fields.Date('End Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    # start_datetime_text = fields.Char('Employee Start Date',   compute='_compute_text_field', store=True)
    # end_datetime_text = fields.Char('Employee End Date', compute='_compute_text_field', store=True)
    duration = fields.Float('Duration by hour', compute='calculate_overtime', readonly=True, store=True)
    overtime = fields.Float('Overtime by hour', compute='calculate_overtime', readonly=True, store=True)
    analytic_account_id = fields.Many2one('account.analytic.account',string="Cost Center/Project", readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('first_approve', 'First Approval'),
                              ('second_approve', 'Second Approval'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], string='Status', default='draft', track_visibility='onchange')
    cost = fields.Float('Total Cost', compute='calculate_overtime', readonly=True, store=True)
    analytic_line_id = fields.Many2one('account.analytic.line', readonly=True,copy=False, track_visibility='onchange')
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', readonly=True)
    show_analytic_fields = fields.Boolean(compute='_compute_show_analytic_fields')
    is_employee = fields.Boolean(compute='_compute_is_employee')
    do_first_approval = fields.Boolean(compute='button_privilege')
    do_second_approval = fields.Boolean(compute='button_privilege')
    do_done = fields.Boolean(compute='button_privilege')
    note = fields.Text('Notes')
    #custom fields
    total_day = fields.Float(compute = 'get_total_day',track_visibility='onchange')
    date_of_overtime_line_id = fields.One2many('date.of.overtime.line','overtime_id',string = "Time Overtime")

    

    #-----------------------------------------CUSTOM-FIELDS-------------------------------------
    tang_ca_ngay_le = fields.Float('Overtime on holiday', compute = 'calculateOvertime')
    tang_ca_ngay_le22 = fields.Float('Overtime on holiday after 22h', compute = 'calculateOvertime')
    tang_ca_ngay_cuoi_tuan = fields.Float('Overtime on weekend day', compute = 'calculateOvertime')
    tang_ca_ngay_cuoi_tuan22 = fields.Float('Overtime on weekend day after 22h', compute = 'calculateOvertime')
    tang_ca_ngay_thuong = fields.Float('Overtime on normal day', compute = 'calculateOvertime')
    tang_ca_ngay_thuong22 = fields.Float('Overtime on normal day after 22h', compute = 'calculateOvertime')
    
    global_leave = []
    working_time = []

    # @api.depends('end_datetime','start_datetime','employee_id')
    # def _compute_text_field(self):
    #     record_lang = self.env['res.lang'].search([("code", "=", self._context['lang'])], limit=1)
    #     format_date, format_time = record_lang.date_format,record_lang.time_format
    #     strftime_pattern = (u"%s %s" % (format_date,format_time))
    #     for rec in self:
    #         if rec.end_datetime and rec.employee_id:
    #             to_dt = fields.Datetime.from_string(rec.end_datetime).replace(tzinfo=UTC)
    #             to_dt = to_dt.astimezone(timezone(rec.employee_id.tz))
    #             rec.end_datetime_text = to_dt.strftime(strftime_pattern)
                
    #         else:
    #             rec.end_datetime_text = False
    #         if rec.start_datetime and rec.employee_id:
    #             from_dt = fields.Datetime.from_string(rec.start_datetime).replace(tzinfo=UTC)
    #             from_dt = from_dt.astimezone(timezone(rec.employee_id.tz))
    #             rec.start_datetime_text =  from_dt.strftime(strftime_pattern)
    #         else:
    #             rec.start_datetime_text = False
        
    @api.multi
    @api.depends('state')
    def button_privilege(self):
        employee_id = self.env['hr.employee'].search([('user_id','=',self._uid)],limit = 1)
        if employee_id:
            for rec in self:
                if employee_id.id == rec.employee_id.parent_id.id:
                    rec.do_first_approval = True
                if employee_id.id == rec.employee_id.department_id.manager_id.id:
                    rec.do_second_approval = True
        ad_mng = self.env.user.has_group('account.group_account_manager') or  self.env.user.has_group('hr_payroll.group_hr_payroll_manager')or  self.env.user.has_group('hr.group_hr_manager')

        if ad_mng:
            self.update({'do_done': True })
            
            
    @api.multi
    @api.depends('state')
    def _compute_is_employee(self):
        is_officer = self.env.user.has_group('hr.group_hr_user')
        self.update({'is_employee': not is_officer })
    
    
    @api.model
    def default_get(self, fields_list):
        res = super(hr_overtime, self).default_get(fields_list)
        employee_id = self.env['hr.employee'].search([('user_id','=',self._uid)],limit = 1)
        res['employee_id'] = employee_id and employee_id.id or False
        return res
        
    @api.multi
    @api.depends('state')
    def _compute_show_analytic_fields(self):
        show_analytic_fields = self.env.user.company_id.overtime_analytic == 'with_entries'
        for rec in self:
            rec.show_analytic_fields = show_analytic_fields
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        res = super(hr_overtime, self).create(vals)
        add_follower = self.env['mail.wizard.invite'].create({'res_model':self._name, 'res_id':res.id,
                                           'partner_ids':[(4, id) for id in self.env.user.company_id.users_to_notify_ot_ids.mapped('partner_id.id') + res.employee_id.mapped('parent_id.user_id.partner_id.id') + res.employee_id.mapped('department_id.manager_id.user_id.partner_id.id')]})
        add_follower.add_followers()
        return res
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You cannon delete confirmed record')
        return super(hr_overtime, self).unlink()
    
    @api.onchange('end_date', 'start_date','employee_id')
    @api.constrains('employee_id', 'end_date', 'start_date')
    def constrains_employee_id(self):
        payslip_obj = self.env['hr.payslip']
        if not (self.employee_id and self.start_date and self.end_date):
            return
        contract_ids = payslip_obj.get_contract(self.employee_id , self.start_date, self.end_date)
        if not contract_ids:
            raise UserError("Please make sure the employee has a running contract.")
    # @api.onchange('end_datetime', 'start_datetime','employee_id')
    # @api.constrains('employee_id', 'end_datetime', 'start_datetime')
    # def constrains_employee_id(self):
    #     payslip_obj = self.env['hr.payslip']
    #     if not (self.employee_id and self.start_datetime and self.end_datetime):
    #         return
    #     contract_ids = payslip_obj.get_contract(self.employee_id , self.start_datetime, self.end_datetime)
    #     if not contract_ids:
    #         raise UserError("Please make sure the employee has a running contract.")
    @api.constrains('end_date','start_date')
    def date_constrains(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise UserError(_('The start date must be before the end date.'))
    # @api.constrains('end_datetime', 'start_datetime')
    # def date_constrains(self):
    #     for rec in self:
    #         if rec.start_datetime and rec.end_datetime and rec.start_datetime > rec.end_datetime:
    #             raise UserError(_('The start date must be before the end date.'))
    #-----------------------------------------CUSTOM CODE-------------------------------------
    #custom luong theo overtime category
    ###
  
    @api.constrains('end_date','start_date')
    def total_day_constrains(self):
        for rec in self:
            total_day =  (rec.end_date - rec.start_date).days
            if rec.start_date and rec.end_date and total_day > 6:
                raise UserError(_('Just set in 7 date'))
    
    

    @api.onchange('date_of_overtime_line_id')
    def conditionTimeOvertime(self):
        for rec_overtime in self.date_of_overtime_line_id:
            if rec_overtime.hour_from < 0.0 :
                rec_overtime.hour_from = 0.0
            elif rec_overtime.hour_from >= 24.0:
                max_time = datetime.time.max
                rec_overtime.hour_from = max_time.hour + max_time.minute/60 + max_time.second/3600
            if rec_overtime.hour_to < 0.0 :
                rec_overtime.hour_to = 0.0
            elif rec_overtime.hour_to >= 24.0:
                max_time = datetime.time.max
                rec_overtime.hour_to = max_time.hour + max_time.minute/60 + max_time.second/3600
    @api.onchange('start_date', 'end_date' , 'date_of_overtime_line_id')
    def conditionDateOvertime(self):
        for rec in self:
            for rec_overtime in rec.date_of_overtime_line_id:
                if rec.start_date and rec.end_date:
                    if rec_overtime.date_overtime < rec.start_date:
                        rec_overtime.date_overtime = rec.start_date
                    elif rec_overtime.date_overtime  > rec.end_date:
                        rec_overtime.date_overtime = rec.end_date
    def get_total_day(self):
        d = self.end_date - self.start_date
        self.total_day = int(d.days)
        #self.total_day = d
    def init_calendar(self):
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        List_global = []
        List_working_time = []
        self_resource_calendar = self.env['resource.calendar'].search([])
        for rec_calendar in self_resource_calendar:
            for i in range(len(rec_calendar.global_leave_ids)):
                from_dt = rec_calendar.global_leave_ids[i].date_from
                to_dt = rec_calendar.global_leave_ids[i].date_to
                from_dt = from_dt.replace(tzinfo=pytz.utc).astimezone(timezone(self.employee_id.tz))
                to_dt = to_dt.replace(tzinfo=pytz.utc).astimezone(timezone(self.employee_id.tz))
                vals = {
                    'dayFrom' : from_dt,
                    'dayTo' : to_dt
                }
                List_global.append(vals)
        for rec_calendar in self_resource_calendar:
            for i in range(len(rec_calendar.attendance_ids)):
                vals = {
                    'name' : rec_calendar.attendance_ids[i].name,
                    'dayOfWeek' : rec_calendar.attendance_ids[i].dayofweek,
                    'hourFrom' : rec_calendar.attendance_ids[i].hour_from,
                    'hourTo': rec_calendar.attendance_ids[i].hour_to,
                    'dayPeriod': rec_calendar.attendance_ids[i].day_period
                }
                List_working_time.append(vals)
            break
        
        hr_overtime.global_leave = List_global
        hr_overtime.working_time = List_working_time
    def convertWorkingTime(self):
        global_leave = []
        #get first element
        i = 0
        while(i < len(hr_overtime.working_time)):
            startMorning = 0
            endMorning = 0
            startAfternoon = 0
            endAfternoon = 0
            dayOfWeek = hr_overtime.working_time[i].get('dayOfWeek')       
            startMorning = hr_overtime.working_time[i].get('hourFrom')
            endMorning = hr_overtime.working_time[i].get('hourTo')
            if i+1 < len(hr_overtime.working_time):
                i += 1
                if hr_overtime.working_time[i].get('dayOfWeek') == dayOfWeek:
                    startAfternoon = hr_overtime.working_time[i].get('hourFrom')
                    endAfternoon = hr_overtime.working_time[i].get('hourTo')
                else:
                    i+=1
            i+=1
            global_leave.append({
                'dayOfWeek' : dayOfWeek,
                'startMorning': startMorning,
                'endMorning' : endMorning,
                'startAfternoon':startAfternoon,
                'endAfternoon': endAfternoon
            })
        return global_leave
    def getListWorkingTime(self):
        result = []
        for rec in self.convertWorkingTime():
            result.append(rec.get('dayOfWeek'))
        return result
    def isGlobalLeave(self,current):
        if len(hr_overtime.global_leave) == 0:
            return False
        else:
            for d in range(len(hr_overtime.global_leave)):
                dayGlobalFrom = hr_overtime.global_leave[d].get('dayFrom')
                dayGlobalTo = hr_overtime.global_leave[d].get('dayTo')
                if dayGlobalFrom.date() <= current and current <= dayGlobalTo.date():
                    return True
            return False
    def splitByTime(self,start,end,anchorTime,morning = [],afternoon = []):
        #Caculate the hours worked in a day
        time = 0
        time22 = 0
        if morning:
            if morning[0] == 0 and morning[1] == 0:
                startMorning = morning[0]
                endMorning = morning[1]
            elif start >= morning[1]:
                startMorning = 0
                endMorning = 0
            else:
                if start >= morning[0]:
                    if end <= morning[1]:
                        return time,time22
                    else:
                        startMorning = start
                        endMorning = morning[1]
                else:
                    if end < morning[1]:
                        startMorning = morning[0]
                        endMorning = end
                    else:
                        startMorning = morning[0]
                    endMorning = morning[1]
            durationMorning = endMorning - startMorning
        else:
            durationMorning = 0
            
        if afternoon:
            if afternoon[0] == 0 and afternoon[1] == 0:
                startAfternoon= afternoon[0]
                endAfternoon = afternoon[1]
            elif start >= afternoon[1]:
                startAfternoon = 0
                endAfternoon = 0
            else:
                if start >= afternoon[0]:
                    if end <= afternoon[1]:
                        return time,time22
                    else:
                        startAfternoon = start
                        endAfternoon = afternoon[1]
                else:
                    if end < afternoon[1]:
                        startAfternoon = afternoon[0]
                        endAfternoon = end
                    else:
                        startAfternoon= afternoon[0]
                        endAfternoon = afternoon[1]
            durationAfternoon = endAfternoon - startAfternoon
        else:
            durationAfternoon = 0
        
        if durationMorning == 0 and durationAfternoon == 0:
            return self.splitTimeWithOutWorkingTime(start,end,anchorTime)
        if morning[0] == 0 and morning[1] == 0:
            if  start >= afternoon[1]:
                if end <= anchorTime:
                    time = end - start
                elif start >= anchorTime:
                    time22 = end - start
                else: 
                    time = anchorTime - start
                    time22 = end - anchorTime
            else:
                if end <= anchorTime:
                    time = end - start - durationAfternoon
                elif start >= anchorTime:
                    time22 = end - start
                else: 
                    time = anchorTime - start - durationAfternoon
                    time22 = end - anchorTime
        elif afternoon[0] == 0 and afternoon[1] == 0:
            if  start >= morning[1]:
                if end <= anchorTime:
                    time = end - start
                elif start >= anchorTime:
                    time22 = end - start
                else: 
                    time = anchorTime - start
                    time22 = end - anchorTime
            else:
                if end <= anchorTime:
                    time = end - start - durationMorning
                elif start >= anchorTime:
                    time22 = end - start
                else: 
                    time = anchorTime - start - durationMorning
                    time22 = end - anchorTime 
        elif  start >= afternoon[1]:
            if end <= anchorTime:
                time = end - start
            elif start >= anchorTime:
                time22 = end - start
            else: 
                time = anchorTime - start
                time22 = end - anchorTime
        elif start >= morning[1]:
            if end <= anchorTime:
                time = end - start - durationAfternoon
            else: 
                time = anchorTime - start - durationAfternoon
                time22 = end - anchorTime
        else:
            if end <= anchorTime:
                # if end >= afternoon[1]:
                #     time = end - start - durationAfternoon - durationMorning
                if end >= afternoon[0]:
                    time = end - start - durationMorning - durationAfternoon
                elif end >= morning[0]:
                    time = end - start - durationMorning
                else:
                    time = end - start
            else: 
                time = anchorTime - start - durationAfternoon - durationMorning
                time22 = end - anchorTime
        return time,time22
    def splitTimeWithOutWorkingTime(self,start,end,anchorTime):
        time = 0
        time22 = 0
        if end <= anchorTime:
            time = end - start
        elif start >= anchorTime:
            time22 = end - start
        else:
            time = anchorTime - start
            time22 = end - anchorTime
        return time,time22
    def calculateOvertime(self):
        self.init_calendar()
        workingTime = self.convertWorkingTime()
        checkWorkingTime = self.getListWorkingTime()
        tang_ca_ngay_le = 0.0
        tang_ca_ngay_le22 = 0.0
        tang_ca_ngay_cuoi_tuan = 0.0
        tang_ca_ngay_cuoi_tuan22 = 0.0
        tang_ca_ngay_thuong = 0.0
        tang_ca_ngay_thuong22 = 0.0
        anchorTime = 22
        for rec in self:
            rec.tang_ca_ngay_le = 0.0
            rec.tang_ca_ngay_le22 = 0.0
            rec.tang_ca_ngay_cuoi_tuan = 0.0
            rec.tang_ca_ngay_cuoi_tuan22 = 0.0
            rec.tang_ca_ngay_thuong = 0.0
            rec.tang_ca_ngay_thuong22 = 0.0
            for rec_overtime in rec.date_of_overtime_line_id:
                if self.isGlobalLeave(rec_overtime.date_overtime) == True:
                   tang_ca_ngay_le ,tang_ca_ngay_le22 = self.splitTimeWithOutWorkingTime(rec_overtime.hour_from,rec_overtime.hour_to,anchorTime)
                   rec.tang_ca_ngay_le+= tang_ca_ngay_le
                   rec.tang_ca_ngay_le22 += tang_ca_ngay_le22
                else:
                    for rec_working in workingTime:
                        if rec_overtime.date_overtime.weekday() in [5,6]:
                            if str(rec_overtime.date_overtime.weekday()) not in checkWorkingTime:
                                tang_ca_ngay_cuoi_tuan,tang_ca_ngay_cuoi_tuan22 = self.splitTimeWithOutWorkingTime(rec_overtime.hour_from,rec_overtime.hour_to,anchorTime)
                                rec.tang_ca_ngay_cuoi_tuan+= tang_ca_ngay_cuoi_tuan
                                rec.tang_ca_ngay_cuoi_tuan22 += tang_ca_ngay_cuoi_tuan22
                            else:
                                if str(rec_overtime.date_overtime.weekday()) == rec_working.get('dayOfWeek'):
                                    tang_ca_ngay_cuoi_tuan,tang_ca_ngay_cuoi_tuan22 = self.splitByTime(rec_overtime.hour_from,rec_overtime.hour_to,anchorTime,morning = [rec_working.get('startMorning'),rec_working.get('endMorning')],afternoon = [rec_working.get('startAfternoon'),rec_working.get('endAfternoon')])
                                    rec.tang_ca_ngay_cuoi_tuan+= tang_ca_ngay_cuoi_tuan
                                    rec.tang_ca_ngay_cuoi_tuan22 += tang_ca_ngay_cuoi_tuan22
                        else:
                            if str(rec_overtime.date_overtime.weekday()) not in checkWorkingTime:
                                tang_ca_ngay_thuong,tang_ca_ngay_thuong22 = self.splitTimeWithOutWorkingTime(rec_overtime.hour_from,rec_overtime.hour_to,anchorTime)
                                rec.tang_ca_ngay_thuong+= tang_ca_ngay_thuong
                                rec.tang_ca_ngay_thuong22 += tang_ca_ngay_thuong22
                            else:
                                if str(rec_overtime.date_overtime.weekday()) == rec_working.get('dayOfWeek'):
                                    tang_ca_ngay_thuong,tang_ca_ngay_thuong22 = self.splitByTime(rec_overtime.hour_from,rec_overtime.hour_to,anchorTime,morning = [rec_working.get('startMorning'),rec_working.get('endMorning')],afternoon = [rec_working.get('startAfternoon'),rec_working.get('endAfternoon')])
                                    rec.tang_ca_ngay_thuong+= tang_ca_ngay_thuong
                                    rec.tang_ca_ngay_thuong22 += tang_ca_ngay_thuong22
    
    @api.model
    def is_off_day(self, date_time  , contract, calendar):
        if 'hr.public_holiday' in self.env:
            public_holiday = self.env['hr.leave'].search([('date', '>=', str(date_time)[:10] + ' 00:00:00'),
                                                                   ('date_to', '<=', str(date_time)[:10] + ' 23:59:59'),
                                                                   ('holiday_status_id.is_public_holiday', '=', True),
                                                                   ('state', '=', 'validate'),
                                                                   ('employee_id', '=', contract.employee_id.id)])
            if public_holiday:
                return True
            
        if date_time.weekday() not in calendar:
            return True
        return False
        
    @api.multi
    def done_overtime(self):
        analytic_line_pool = self.env['account.analytic.line']
        timenow = time.strftime('%Y-%m-%d')
        tag = self.env.ref('hr_overtime_management.overtime_tag')
        general_account_id = False
        vals_1 = {'state':'done'}
        if self.show_analytic_fields:
            vals = {
                    'name': _('Overtime for ') + str(self.employee_id.name),
                    'account_id': self.analytic_account_id and self.analytic_account_id.id or False,
                    'tag_ids' : [(6, 0, [tag.id])],
                    'date': timenow,
                    'unit_amount': self.overtime,
                    'general_account_id': self.env.user.company_id.overtime_account_id.id,
                    'amount': self.cost * -1,
                    }
            res = analytic_line_pool.create(vals)
            vals_1['analytic_line_id'] = res.id
        self.write(vals_1)    
        return True
        
    @api.multi
    def confirm(self):
        self.write({'state':'confirmed'})  
        
    @api.multi
    def first_approve(self):
        self.write({'state':'first_approve'})    
        
    @api.multi
    def second_approve(self):
        self.write({'state':'second_approve'})

    @api.multi
    def draft(self): 
        self.write({'state':'draft'})
        
    @api.multi
    def cancel(self):
        self.analytic_line_id.unlink()
        self.write({'state':'cancel'})
    
    
     
class hr_payslip_inhe(models.Model): 
    _inherit = 'hr.payslip'
    
    
    @api.multi
    def refund_sheet(self):
        for payslip in self:
            overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('date', '>=', self.date_from),
                                                                ('date', '<=', self.date_to)])
            overtime_ids.write({'payslip_id':False})
        return super(hr_payslip_inhe, self).refund_sheet()
    
    @api.multi
    def action_payslip_done(self):
        res = super(hr_payslip_inhe, self).action_payslip_done()
        for payslip in self.filtered(lambda x: not x.credit_note):
            overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', payslip.employee_id.id),
                                                                ('date', '>=', payslip.date_from),
                                                                ('date', '<=', payslip.date_to)])
            
            overtime_ids.write({'payslip_id':payslip.id})
        
        return res
    
    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = super(hr_payslip_inhe, self).get_inputs(contracts, date_from, date_to)
        ot_obj = self.env['hr.overtime']
        if self.employee_id and date_from and date_to and contracts:
            contract =  contracts[0]
            
            if self.env.user.company_id.overtime_type == 'request':
                overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('date', '>=', fields.Date.to_string(date_from)),
                                                                ('date', '<=', fields.Date.to_string(date_to)),
                                                                ('payslip_id', '=', False)])
                if overtime_ids:
                    total_overtimes = 0.0
                    total_overtimes_holiday = 0.0
                    for rec in overtime_ids:
                        total_overtimes += rec.cost
                             
                    if total_overtimes:
                        vals = {'name': 'Overtime', 'code': 'OTN', 'amount': total_overtimes, 'contract_id': contract.id}
                        res += [vals]
            elif self.env.user.company_id.overtime_type == 'attendance':
                att_ids = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id),
                                                  ('check_in', '>=', fields.Date.to_string(date_from)),
                                                  ('check_in', '<', fields.Date.to_string(date_to) + ' 24:00:00'),
                                                  ('check_out', '!=', False)])
                overtime_list = []
                for att_id in att_ids:
                    check_in = fields.Datetime.from_string(att_id.check_in).replace(tzinfo=UTC)
                    check_in = check_in.astimezone(timezone(att_id.employee_id.tz))
                    check_out = fields.Datetime.from_string(att_id.check_out).replace(tzinfo=UTC)
                    check_out = check_out.astimezone(timezone(att_id.employee_id.tz))
                    overtime  = ot_obj._calculate_durations( check_in, check_out,contract)
                    if overtime:
                        overtime_list.extend(overtime)
                if overtime_list:
                    cost_by_hour = contract.wage / 30.4 / 8
                    work_overtiem = contract.resource_calendar_id.overtime_work_days
                    off_overtiem = contract.resource_calendar_id.overtime_off_days
                    toata_hours = 0.0
                    for i in overtime_list:
                        toata_hours += i[0] * (off_overtiem if i[1] else work_overtiem)
                    vals = {'name': 'Overtime %0.2f Hour(s)'%toata_hours, 'code': 'OTN', 'amount': toata_hours * cost_by_hour, 'contract_id': contract.id}
                    res += [vals]
                
        return res
        
#start custom class
class  date_of_overtime_line(models.Model):
    _name = "date.of.overtime.line"

    overtime_id = fields.Many2one('hr.overtime', 'Overtime')
    date_overtime = fields.Date("Date overtime",required=True)
    hour_from = fields.Float("Overtime start",required=True,default = 0.0)
    hour_to = fields.Float("Overtime end",required=True,default =0.0)
#end custom class
