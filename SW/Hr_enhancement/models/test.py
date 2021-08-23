from odoo import api, fields, models, tools,_
from odoo.exceptions import except_orm, ValidationError ,UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta , date
import math
from num2words import num2words
from odoo.exceptions import Warning
from odoo.tools import float_utils, float_compare ,pycompat ,email_re, email_split, email_escape_char, float_is_zero, date_utils

from odoo.tools.misc import format_date



#HR Contract and Payroll Customize Part
class Hrcontractscus(models.Model):
    _inherit = 'hr.contract'

    hr_allowance_line_ids = fields.One2many('hr.allowance.line','contract_id',string='HR Allowance')
    hr_total_wage = fields.Float('Total Salary',compute="_total_wage")

    @api.multi
    def _total_wage(self):
        for rec in self:
            x = rec.wage
            for l in rec.hr_allowance_line_ids:
                x = x + l.amt
            rec.hr_total_wage = x


class HRallowanceLine(models.Model):
    _name = 'hr.allowance.line'

    contract_id = fields.Many2one('hr.contract')
    rule_type = fields.Many2one('hr.salary.rule',string="Allowance Rule")
    code = fields.Char('Code',related="rule_type.code",store=True,readonly=True)
    amt = fields.Float('Amount')

class HRpayrolltran(models.Model):
    _name = 'hr.payroll.transactions'

    state = fields.Selection(string='Status', selection=[
        ('draft','New'),
        ('confirm','Waiting Approval'),
        ('accepted','Approved'),
        ('done','Done'),
        ('paid','Paid'),
        ('cancelled','Refused')],
        copy=False, index=True, readonly=True,default="draft")
    date_from = fields.Date('Date')
    date_to = fields.Date('To')
    date = fields.Date('Date')
    name = fields.Char('Description')
    payroll_tran_line = fields.One2many('hr.payroll.transactions.line','payroll_tran_id',string='Payroll Transactions')

    @api.multi
    def unlink(self):
        for line in self:
            if line.state in ['paid', 'done']:
                raise UserError(_('Cannot delete a transaction which is in state \'%s\'.') % (line.state,))
        return super(HRpayrolltran, self).unlink()

    @api.multi
    def loans_confirm(self):
        for rec in self:
            for l in rec.payroll_tran_line:
                l.state = 'accepted'
        return self.write({'state': 'done'})

    @api.multi
    def loans_accept(self):
        return self.write({'state': 'done'})

    @api.multi
    def loans_refuse(self):
        return self.write({'state': 'cancelled'})

    @api.multi
    def loans_set_draft(self):
        return self.write({'state': 'draft'})
            

class HRpayrolltranLine(models.Model):
    _name = 'hr.payroll.transactions.line'

    payroll_tran_id = fields.Many2one('hr.payroll.transactions')
    employee_id = fields.Many2one('hr.employee',string="Employee",required=True)
    timesheet_cost = fields.Float('Timesheet Cost')
    number_of_hours = fields.Float('No of Hours')
    tran_note = fields.Char('Transaction')
    allowance = fields.Float('Allowance')
    deduction = fields.Float('Deduction')
    payroll_item = fields.Many2one('hr.salary.rule',string="Payroll Item",required=True)
    analytic_account = fields.Many2one('account.analytic.account',string="Analytic Account")
    state = fields.Selection(string='Status', selection=[
        ('draft','New'),
        ('cancelled','Refused'),
        ('confirm','Waiting Approval'),
        ('accepted','Approved'),
        ('done','Waiting Payment'),
        ('paid','Paid')],readonly=True)

    @api.onchange('number_of_hours')
    def _get_amount(self):
        for rec in self:
            rec.timesheet_cost = rec.employee_id.timesheet_cost
            if rec.payroll_item.payroll_rate :
                rec.allowance = rec.number_of_hours * rec.timesheet_cost * rec.payroll_item.payroll_rate
            else:
                rec.allowance = rec.number_of_hours * rec.timesheet_cost
            

class HrSalaryRulecus(models.Model):
    _inherit = 'hr.salary.rule'

    od_payroll_item = fields.Boolean('Payroll Item',default=False)
    payroll_rate = fields.Float('Rate')

class HrPayslipcus(models.Model):
    _inherit = 'hr.payslip'

    hr_variance_line_id = fields.One2many('hr.variance.line','payslip_id',string="Variance")

    @api.multi
    def unlink(self):
        for rec in self:
            if any(self.filtered(lambda payslip: payslip.state not in ('draft', 'cancel'))):
                raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
            if rec.state == 'draft':
                if rec.hr_variance_line_id:
                    raise UserError(_('You cannot delete a payslip which have payroll transaction(Variance)!'))
        return super(HrPayslipcus, self).unlink()

class HrVarianceLine(models.Model):
    _name = 'hr.variance.line'

    payslip_id = fields.Many2one('hr.payslip')
    tran_id = fields.Many2one('hr.payroll.transactions',string="Transaction")
    rule_id = fields.Many2one('hr.salary.rule',string="Rule")
    date_value = fields.Date('Date')
    tran_note = fields.Char('Transaction Note')
    amount = fields.Float('Amount')

class HrPayslipEmployeescus(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        # add payroll transaction
        
        datas = {}
        obj = self.env['hr.payroll.transactions'].search([('date_from','>=',from_date),('date_from','<=',to_date)])
        # add payroll transaction
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            # add payroll transaction
            invoice_line = []
            for l in obj:
                if l.state == 'done':
                    for k in l.payroll_tran_line:
                        if k.state != 'paid':
                            if k.employee_id.id == employee.id :
                                datas = {
                                    'tran_id':l.id,
                                    'rule_id':k.payroll_item.id,
                                    'date_value':l.date_from,
                                    'tran_note':k.tran_note,
                                    'amount':k.allowance,
                                }
                                invoice_line.append((0, 0, datas))
                                k.state = 'paid'
                            else:
                                continue
                        else:
                            continue
                else:
                    continue

            
            
            # add payroll transaction
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'hr_variance_line_id': invoice_line,
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
            }
            payslips += self.env['hr.payslip'].create(res)
        # for l in obj:
        #         l.state = 'paid'
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}

    # view of payroll transaction Report
class HrPayrollTranSheetView(models.Model):
    _name = 'hr.payroll.tran.sheet.view'
    _description = "Payroll transaction Report"
    _auto = False

    amount = fields.Float('Amount')
    date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee',string="Employee")
    payroll_item = fields.Many2one('hr.salary.rule',string="Payroll Item")
    tran = fields.Char('Transaction')
    description = fields.Char('Description')

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
                SELECT 
                    min(ptl.id) as id,
                    ptl.employee_id,
                    ptl.payroll_item,
                    ptl.tran_note as tran,
                    ptl.allowance as amount,
                    pt.date_from as date,
                    pt.name as description
                    
        """
        return select_str

    def _from(self):
        from_str = """
            hr_payroll_transactions_line ptl
                LEFT JOIN hr_payroll_transactions pt on (ptl.payroll_tran_id = pt.id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                ptl.employee_id,
                ptl.payroll_item,
                ptl.tran_note,
                ptl.allowance,
                pt.date_from,
                pt.name
        """
        return group_by_str

    # view of payroll transaction Report

    # view of Salary Sheet
class HrSalarySheetView(models.Model):
    _name = 'hr.salary.sheet.view'
    _description = "Salary Sheet"
    _auto = False

    # abs_deduction = fields.Float('Absent')
    basic = fields.Float('Basic')
    hra = fields.Float('Housing')
    ot_allowance = fields.Float('OT Allowance')
    allowances_value = fields.Float('Allowances')
    additions = fields.Float('Additions')
    deductions = fields.Float('Deductions')
    other_allowance = fields.Float('Other Allowance')
    # expenses = fields.Float('Expenses')
    fine_deduction = fields.Float('Fine')
    # food_allowance = fields.Float('FA')
    gross = fields.Float('Gross')
    loan_deduction = fields.Float('Loan')
    net_salary = fields.Float('Net Salary')
    present = fields.Float('Present')
    trans_allowance = fields.Float('Transport Allowance')
    # traveling_allowance = fields.Float('Traveling Allowance')
    payslip_days = fields.Float('Payslip Days')
    structure_id = fields.Many2one('hr.payroll.structure',string="Salary Structure")
    type_id = fields.Many2one('hr.contract.type',string="Contract Type")
    job_id = fields.Many2one('hr.job',string="Designation")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    department_id = fields.Many2one('hr.department',string="Department")
    identification = fields.Char('Identification No.')
    batch_name = fields.Char('Batch')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
                SELECT row_number() OVER (ORDER BY hr_payslip.id) AS id,
                    hr_payslip.employee_id,
                    hr_employee.identification_id AS identification,
                    hr_payslip.struct_id AS structure_id,
                    hr_employee.department_id,
                    hr_employee.job_id,
                    hr_contract.type_id,
                    hr_payslip.date_from,
                    hr_payslip.date_to,
                    hr_payslip.date_to - hr_payslip.date_from + 1 AS payslip_days,
                    hr_payslip_run.name AS batch_name,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'BASIC'::text) AS basic,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'HRA'::text) AS hra,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'OTH'::text) AS other_allowance,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'OT'::text) AS ot_allowance,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'ALWCE'::text) AS allowances_value,
                        
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'ADTNS'::text) AS additions,

                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'DED'::text) AS deductions,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'TRA'::text) AS trans_allowance,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'LOAN'::text) AS loan_deduction,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'FINE'::text) AS fine_deduction,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'GROSS'::text) AS gross,
                    ( SELECT sum(hr_payslip_worked_days.number_of_days) AS sum
                        FROM hr_payslip_worked_days
                        WHERE hr_payslip_worked_days.payslip_id = hr_payslip.id AND hr_payslip_worked_days.code::text = 'WORK100'::text) AS present,
                    ( SELECT sum(hr_payslip_line.total) AS sum
                        FROM hr_payslip_line
                        WHERE hr_payslip_line.slip_id = hr_payslip.id AND hr_payslip_line.code::text = 'NET'::text) AS net_salary
                    
        """
        return select_str

    def _from(self):
        from_str = """
            hr_payslip
                JOIN hr_contract on (hr_contract.id = hr_payslip.contract_id)
                JOIN hr_employee on (hr_employee.id = hr_contract.employee_id)
                JOIN hr_payroll_structure on (hr_payroll_structure.id = hr_contract.struct_id)
                JOIN hr_payslip_run on (hr_payslip_run.id = hr_payslip.payslip_run_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                hr_payslip.id,
                hr_payslip.employee_id,
                hr_payslip_run.name,
                hr_employee.department_id,
                hr_employee.job_id,
                hr_payslip.date_from,
                hr_payslip.date_to,
                hr_contract.type_id, 
                hr_employee.identification_id, 
                hr_payslip.struct_id
        """
        return group_by_str

    # view of Salary Sheet
class LeaveAnalysis(models.Model):
    _name = 'leave.analysis'
    _description = "Leaves Analysis"
    _auto = False

    # abs_deduction = fields.Float('Absent')
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    holiday_status_id = fields.Many2one('hr.leave.type',string='Leaves Type')
    # number_of_days = fields.Float('No of Days')
    # the_month = fields.Datetime('Date')
    total_leave_days = fields.Float('Total Leaves Days')
    total_allocated_days = fields.Float('Total Allocated Days')
    pending_leaves = fields.Float('Pending Leaves')

    # @api.depends('total_leave_days','total_allocated_days')
    # def _pending_leave(self):
    #     for rec in self:
    #         rec.pending_leave = rec.total_allocated_days - rec.total_leave_days

    

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr,'leave_analysis')
        self.env.cr.execute("""CREATE or REPLACE view leave_analysis as (
                SELECT row_number() over(ORDER BY e.id) as id,
                        e.id as employee_id,
                        l.holiday_status_id,
                        sum(l.number_of_days) as total_leave_days, 
                        (select sum(a.number_of_days)
                        from hr_leave_allocation a
                        where e.id = a.employee_id
                        ) as total_allocated_days,
                        ((select sum(a.number_of_days)
                            from hr_leave_allocation a
                            where e.id = a.employee_id
                            ) - sum(l.number_of_days)) as pending_leaves
                        from hr_employee e,
                            hr_leave l
                        where 	e.id=l.employee_id
                    group by e.id, l.holiday_status_id
            );""" )
   
#HR Contract and Payroll Customize Part



# Employee Master edits 
class HrEmployeescus(models.Model):
    _inherit = 'hr.employee'

    join_date = fields.Datetime('Date of Join')
    airfare = fields.Float('Airfare')
    fax_ch = fields.Char('Fax')
    uid_num = fields.Char('UID Number')
    pass_expiry_date = fields.Date('Passport Expiry Date')
    airticket_count = fields.Integer(compute='_airticket_count', string='# Airtickets')
    leaves_count_2 = fields.Float('Number of Leaves', compute='_compute_leaves_count2')
    emirates_id = fields.Char('Emirates ID')
    emirates_id_expiry_date = fields.Date('Emirates ID Expiry Date')
    allow_sick_leave = fields.Float('Allowed Sick Leave Days',default=0)

    def _get_date_start_work(self):
        return self.join_date

    @api.multi
    def _compute_leaves_count2(self):
        for rec in self:
            x = 0.0
            all_leaves = self.env['hr.leave.report'].search([('employee_id', '=', rec.id)])
            for l in all_leaves:
                if l.number_of_days < 0.0 and l.state == 'validate':
                    x = x + l.number_of_days
            rec.leaves_count_2 = x

    @api.multi
    def _airticket_count(self):
        for each in self:
            air_ids = self.env['hr.airticket'].sudo().search([('name', '=', each.id)])
            each.airticket_count = len(air_ids)


    @api.multi
    def airticket_view(self):
        self.ensure_one()
        domain = [
            ('name', '=', self.id)]
        vals = {
            'default_name': self.id,
            'default_depart': self.department_id.id,
            'default_designation': self.job_id.id,
            'default_join_date': self.join_date,
            'default_Airfare': self.airfare
        }
        return {
            'name': _('Airtickets'),
            'domain': domain,
            'res_model': 'hr.airticket',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Airticket
                        </p>'''),
            'limit': 80,
            'context': vals,
        }

    @api.multi
    @api.onchange('country_id')
    def _airfare_value(self):
        for rec in self:
            rec.airfare = rec.country_id.airfare

    @api.multi
    def document_view(self):
        action = self.env.ref('Hr_enhancement.hr_employee_document_cus_action2').read()[0]
        return action

class HRAirticket(models.Model):
    _name = 'hr.airticket'
    _description = 'HR Air Ticket'


    name = fields.Many2one('hr.employee',string="Employee Name")
    depart = fields.Many2one('hr.department',string="Department")
    designation = fields.Many2one('hr.job',string="Designation")
    join_date = fields.Date('Join Date')
    Airfare = fields.Float('Airfare')
    amount = fields.Float('Ticket Amount')
    ticket_date = fields.Date('Ticket Issued Date')
    remarks = fields.Text('Remarks')


class Countriesscus(models.Model):
    _inherit = 'res.country'

    airfare = fields.Float('Airfare')

# Employee Master edits 



class hrleaveUpdate(models.Model):
    _inherit = "hr.leave"

    allow_sick_changed = fields.Boolean('Alloe check',default=False)

    @api.multi
    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()

        # Sick leave part
        if self.holiday_status_id.name == 'Sick':
                self.allow_sick_changed = True
                self.employee_id.allow_sick_leave += self.number_of_days_display 
        #Sick leave part

        channel_all_employees = self.env.ref('Hr_enhancement.channel_all_leave_status').read()[0]
        template_new_employee = self.env.ref('Hr_enhancement.email_template_data_applicant_leaves').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            message = """Leave with type %s come From %s in %s department between dates  %s to %s 
            get Approved by %s """  % (self.holiday_status_id.name, self.employee_id.name, self.department_id.name,self.request_date_from,self.request_date_to,self.env.user.name)
            channel_id.message_post(body=message, subject=subject,subtype='mail.mt_comment')
            
        return True


    @api.multi
    def action_refuse(self):
        
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
                channel_all_employees = self.env.ref('Hr_enhancement.channel_all_leave_status').read()[0]
                template_new_employee = self.env.ref('Hr_enhancement.email_template_data_applicant_leaves').read()[0]
                # raise ValidationError(_(template_new_employee))
                if template_new_employee:
                    # MailTemplate = self.env['mail.template']
                    body_html = template_new_employee['body_html']
                    subject = template_new_employee['subject']
                    # raise ValidationError(_('%s %s ') % (body_html,subject))
                    ids = channel_all_employees['id']
                    channel_id = self.env['mail.channel'].search([('id', '=', ids)])
                    message = """Leave with type %s come From %s in %s department between dates  %s to %s 
                    get Refused by %s """  % (self.holiday_status_id.name, self.employee_id.name, self.department_id.name,self.request_date_from,self.request_date_to,self.env.user.name)
                    channel_id.message_post(body=message, subject=subject,subtype='mail.mt_comment')
                    
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
                channel_all_employees = self.env.ref('Hr_enhancement.channel_all_leave_status').read()[0]
                template_new_employee = self.env.ref('Hr_enhancement.email_template_data_applicant_leaves').read()[0]
                # raise ValidationError(_(template_new_employee))
                if template_new_employee:
                    # MailTemplate = self.env['mail.template']
                    body_html = template_new_employee['body_html']
                    subject = template_new_employee['subject']
                    # raise ValidationError(_('%s %s ') % (body_html,subject))
                    ids = channel_all_employees['id']
                    channel_id = self.env['mail.channel'].search([('id', '=', ids)])
                    message = """Leave with type %s come From %s in %s department between dates  %s to %s 
                    get Refused by %s """  % (self.holiday_status_id.name, self.employee_id.name, self.department_id.name,self.request_date_from,self.request_date_to,self.env.user.name)
                    channel_id.message_post(body=message, subject=subject,subtype='mail.mt_comment')
                    
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()

            # Sick leave part
            if holiday.holiday_status_id.name == 'Sick':
                if holiday.allow_sick_changed == True:
                    holiday.employee_id.allow_sick_leave -= holiday.number_of_days_display 
            # Sick leave part
        self._remove_resource_leave()
        self.activity_update()
        
        return True



# expense changes
class hrexpenseUpdate(models.Model):
    _inherit = "hr.expense"

    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], default='company_account', states={'done': [('readonly', True)], 'post': [('readonly', True)], 'submitted': [('readonly', True)]}, string="Paid By")
    is_vendor = fields.Boolean('Is Vendor Expense',default=False)
    vendor_id = fields.Many2one('res.partner','Vendor')
    # employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)], 'refused': [('readonly', False)]}, default=_default_employee_id, domain=lambda self: self._get_employee_id_domain())
    
    @api.multi
    def action_submit_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        return {
            'name': _('New Expense Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_employee_id': self[0].employee_id.id,
                'default_is_vendor': self.is_vendor,
                'default_vendor_id': self.vendor_id.id,
                'default_name': todo[0].name if len(todo) == 1 else ''
            }
        }

    @api.multi
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            if expense.is_vendor == False:
                move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
                partner_id = expense.employee_id.address_home_id.commercial_partner_id.id
            else:
                move_line_name = expense.vendor_id.name + ': ' + expense.name.split('\n')[0][:64]
                partner_id = expense.vendor_id.id
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            

            # source move line
            amount = taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount -= move_line_src['debit']
            total_amount_currency -= move_line_src['amount_currency'] or move_line_src['debit']

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_line_id': tax['id'],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense



    @api.multi
    def action_move_create(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        move_group_by_sheet = self._get_account_move_by_sheet()

        move_line_values_by_expense = self._get_account_move_line_values()

        for expense in self:
            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id != company_currency

            # get the account move of the related sheet
            move = move_group_by_sheet[expense.sheet_id.id]

            # get move line values
            move_line_values = move_line_values_by_expense.get(expense.id)
            move_line_dst = move_line_values[-1]
            total_amount = move_line_dst['debit'] or -move_line_dst['credit']
            total_amount_currency = move_line_dst['amount_currency']

            # create one more move line, a counterline for the total on payable account
            if expense.payment_mode == 'company_account':
                if not expense.sheet_id.bank_journal_id.default_credit_account_id:
                    raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.sheet_id.bank_journal_id.name))
                journal = expense.sheet_id.bank_journal_id
                # create payment
                payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
                journal_currency = journal.currency_id or journal.company_id.currency_id
                if expense.is_vendor == False:
                    payment = self.env['account.payment'].create({
                        'payment_method_id': payment_methods and payment_methods[0].id or False,
                        'payment_type': 'outbound' if total_amount < 0 else 'inbound',
                        'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
                        'partner_type': 'supplier',
                        'journal_id': journal.id,
                        'payment_date': expense.date,
                        'state': 'reconciled',
                        'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
                        'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
                        'name': expense.name,
                    })
                else:
                    payment = self.env['account.payment'].create({
                        'payment_method_id': payment_methods and payment_methods[0].id or False,
                        'payment_type': 'outbound' if total_amount < 0 else 'inbound',
                        'partner_id': expense.vendor_id.id,
                        'partner_type': 'supplier',
                        'journal_id': journal.id,
                        'payment_date': expense.date,
                        'state': 'reconciled',
                        'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
                        'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
                        'name': expense.name,
                    })
                move_line_dst['payment_id'] = payment.id

            # link move lines to move, and move to expense sheet
            move.with_context(dont_create_taxes=True).write({
                'line_ids': [(0, 0, line) for line in move_line_values]
            })
            expense.sheet_id.write({'account_move_id': move.id})

            if expense.payment_mode == 'company_account':
                expense.sheet_id.paid_expense_sheets()

        # post the moves
        for move in move_group_by_sheet.values():
            move.post()

        return move_group_by_sheet

class hrexpenseSheetUpdate(models.Model):
    _inherit = "hr.expense.sheet"

    is_vendor = fields.Boolean('Is Vendor Expense',default=False)
    vendor_id = fields.Many2one('res.partner','Vendor')
# expense changes


# view of contract Sheet
class HrContractSheetView(models.Model):
    _name = 'hr.contract.sheet.view'
    _description = "Contract Sheet"
    _auto = False

    basic = fields.Float('Basic')
    hra = fields.Float('Housing')
    air_ticket = fields.Float('Air Ticket Allowance')
    ot_allowance = fields.Float('OT Allowance')
    allowances_value = fields.Float('Allowances')
    additions = fields.Float('Additions')
    deductions = fields.Float('Deductions')
    other_allowance = fields.Float('Other Allowance')
    fine_deduction = fields.Float('Fine')
    gross = fields.Float('Gross')
    loan_deduction = fields.Float('Loan')
    net_salary = fields.Float('Net Salary')
    present = fields.Float('Present')
    wage = fields.Float('Wage')
    trans_allowance = fields.Float('Transport Allowance')
    type_id = fields.Many2one('hr.contract.type',string="Contract Type")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    contract_name = fields.Char('Contract Name')
    total = fields.Char('Total Salary' ,compute='_get_total')

    @api.multi
    def _get_total(self):
        for rec in self:
            rec.total = rec.wage + rec.basic + rec.hra + rec.air_ticket + rec.ot_allowance + rec.allowances_value + rec.additions + rec.deductions + rec.other_allowance + rec.fine_deduction + rec.gross + rec.loan_deduction + rec.net_salary + rec.present + rec.trans_allowance

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
                SELECT row_number() OVER (ORDER BY hr_employee.id) AS id,
                       hr_contract.employee_id,
                       hr_contract.wage AS wage,
                       hr_contract.name AS contract_name,
                        hr_contract.type_id,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'BASIC'::text) AS basic,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'HRA'::text) AS hra,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'OTH'::text) AS other_allowance,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'OT'::text) AS ot_allowance,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'ALWCE'::text) AS allowances_value,
                                
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'ADTNS'::text) AS additions,

                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'DED'::text) AS deductions,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'TRA'::text) AS trans_allowance,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'LOAN'::text) AS loan_deduction,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'FINE'::text) AS fine_deduction,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'GROSS'::text) AS gross,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'WORK100'::text) AS present,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'NET'::text) AS net_salary,
                        ( SELECT sum(hr_allowance_line.amt) AS sum
                            FROM hr_allowance_line
                            WHERE hr_allowance_line.contract_id = hr_contract.id AND hr_allowance_line.code::text = 'AIR'::text) AS air_ticket
                    
        """
        return select_str

    def _from(self):
        from_str = """
            hr_contract
                JOIN hr_employee on (hr_employee.id = hr_contract.employee_id)
                
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            WHERE hr_contract.state in ('open','pending')
            GROUP BY
				hr_contract.id,
                hr_employee.id,
                hr_contract.wage,
				hr_contract.employee_id,
                hr_contract.type_id,
                hr_contract.name
        """
        return group_by_str

    # view of contract Sheet



