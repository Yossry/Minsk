from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from random import choice
from string import digits
from odoo.addons.resource.models.resource import float_to_time


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["mail.activity.mixin", "hr.employee"]

    def name_get(self):
        return super(
            HrEmployee, self.with_context(not_display_company=True)
        ).name_get()

    def _default_personal_identifier(self):
        pid = None
        while not pid or self.env["hr.employee"].search(
            [("personal_identifier", "=", pid)]
        ):
            pid = "".join(choice(digits) for i in range(8))
        return pid

    partner_id = fields.Many2one(
        "res.partner", required=True, store=True, string="Related partner"
    )
    name = fields.Char(compute=False, related="partner_id.name", readonly=True)
    firstname = fields.Char(related="partner_id.firstname")
    lastname = fields.Char(related="partner_id.lastname")
    lastname2 = fields.Char(related="partner_id.lastname2")

    identification_id_expiration = fields.Date(string="Expiration Date")
    user_id = fields.Many2one(
        readonly=True, compute="_compute_user", store=True
    )
    personal_identifier = fields.Char(
        string="Work's Personal ID",
        default=lambda r: r._default_personal_identifier(),
        readonly=True,
        copy=False,
    )
    personal_email = fields.Char(string="Personal Email")

    work_email = fields.Char(related="partner_id.email", store=True)

    personal_phone = fields.Char(string="Phone", related="partner_id.mobile")
    personal_mobile = fields.Char(related="partner_id.phone", string="Mobile")

    show_info = fields.Boolean(
        "Able to see Private Info", compute="_compute_show_info"
    )

    parent_id = fields.Many2one(
        compute="_compute_department_parent_id", readonly=True, store=True
    )
    company_id = fields.Many2one(
        related="contract_id.company_id", readonly=True
    )
    working_hours_type = fields.Selection(
        string="Working Hours Type",
        selection=[
            ("full", "Full Time"),
            ("part", "Part time"),
            ("reduced", "Reduced"),
        ],
        related="contract_id.working_hours_type",
        readonly=True,
    )

    percentage_of_reduction = fields.Float(
        string="Percentage of reduction",
        related="contract_id.percentage_of_reduction",
        readonly=True,
    )
    contract_type_id = fields.Many2one(
        string="Contract Type", related="contract_id.type_id", readonly=True
    )
    laboral_category_id = fields.Many2one(
        "hr.laboral.category",
        related="contract_id.laboral_category_id",
        readonly=True,
    )

    locker = fields.Char(string="Locker")
    manager = fields.Boolean(compute="_compute_is_manager", readonly=True)

    # groups
    address_home_id = fields.Many2one(groups="base.group_user")
    country_id = fields.Many2one(groups="base.group_user")
    gender = fields.Selection(groups="base.group_user")
    marital = fields.Selection(groups="base.group_user")
    birthday = fields.Date(groups="base.group_user")
    ssnid = fields.Char(groups="base.group_user")
    sinid = fields.Char(groups="base.group_user")
    identification_id = fields.Char(
        groups="base.group_user",
        related="partner_id.vat",
        readonly=False,
        string="DNI/NIE",
    )
    passport_id = fields.Char(groups="base.group_user")
    permit_no = fields.Char(groups="base.group_user")
    visa_no = fields.Char(groups="base.group_user")
    visa_expire = fields.Date(groups="base.group_user")
    children = fields.Integer(
        groups="base.group_user", compute="_compute_children_count", store=True
    )

    today_schedule = fields.Char(
        compute="_compute_today_schedule", readonly=True
    )

    contract_id = fields.Many2one(store=True)
    turn = fields.Char(related="contract_id.turn")
    contract_notes = fields.Text()

    address_id = fields.Many2one(string="Center")
    work_location = fields.Char(string="Location")

    prl_ids = fields.One2many("hr.employee.prl", "employee_id")

    @api.depends("department_id", "department_id.manager_id")
    def _compute_department_parent_id(self):
        for record in self:
            if record.department_id:
                manager_id = record.department_id.manager_id
                record.parent_id = (
                    manager_id if (manager_id != record) else False
                )
            else:
                record.parent_id = False

    @api.depends("contract_ids")
    def _compute_contract_id(self):
        if self.env.context.get("execute_old_update", False):
            return super()._compute_contract_id()
        Contract = self.env["hr.contract"]
        for employee in self:
            employee.contract_id = Contract.search(
                [("employee_id", "=", employee.id), ("state", "!=", "draft")],
                order="date_start desc",
                limit=1,
            )

    @api.multi
    def _compute_today_schedule(self):
        public_holidays = self.env["hr.holidays.public"]
        today = fields.Date.today()
        day_date = fields.Date.from_string(today)
        now = fields.Datetime.now()
        for record in self:
            domain = [
                ("date_from", "<=", now),
                ("date_to", ">=", now),
                ("employee_id", "=", record.id),
                ("state", "=", "validate"),
            ]
            personal_holidays = self.env["hr.leave"].search(domain, limit=1)
            if personal_holidays:
                date_from = fields.Date.context_today(
                    self, personal_holidays.date_from
                )
                record.today_schedule = _("Out of office since %s" % date_from)
                continue
            if public_holidays.is_public_holiday(day_date, record.id):
                record.today_schedule = _(
                    "Absent today because of public holidays"
                )
                continue

            attendances = record.resource_calendar_id._get_day_attendances(
                day_date, False, False
            )
            if not attendances:
                record.today_schedule = _("This employee doesn't work today")
            elif len(attendances) == 1:
                record.today_schedule = _("Working from %s to %s") % (
                    float_to_time(attendances.hour_from).strftime("%H:%M"),
                    float_to_time(attendances.hour_to).strftime("%H:%M"),
                )
            else:
                message = record.today_schedule = _(
                    "Working from %s to %s"
                ) % (
                    float_to_time(attendances[0].hour_from).strftime("%H:%M"),
                    float_to_time(attendances[0].hour_to).strftime("%H:%M"),
                )
                attendances = attendances[1:]
                for att in attendances[:-1]:
                    message = message + _(", from %s to %s") % (
                        float_to_time(att.hour_from).strftime("%H:%M"),
                        float_to_time(att.hour_to).strftime("%H:%M"),
                    )
                record.today_schedule = message + _(" and from %s to %s") % (
                    float_to_time(attendances[-1].hour_from).strftime("%H:%M"),
                    float_to_time(attendances[-1].hour_to).strftime("%H:%M"),
                )

    @api.depends("relative_ids")
    def _compute_children_count(self):
        child_relation = self.env.ref("hr_employee_relative.relation_child").id
        for record in self:
            record.children = len(
                record.relative_ids.filtered(
                    lambda r: r.relation_id.id == child_relation
                )
            )

    @api.depends("partner_id")
    def _compute_user(self):
        for record in self:
            user_id = self.env["res.users"].search(
                [
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                    ("partner_id", "=", record.partner_id.id),
                ],
                limit=1,
            )
            record.user_id = user_id

    @api.onchange("company_id")
    def _onchange_company(self):
        if not self.env.context.get("use_old_onchange"):
            return super()._onchange_company()
        return {}

    @api.onchange("department_id")
    def _onchange_department(self):
        if not self.env.context.get("use_old_onchange"):
            return super()._onchange_department()
        return {}

    def _update_employee_manager(self, manager_id):
        return

    @api.multi
    def toggle_active(self):
        for record in self:
            active = not record.active
            record.active = active
            contracts = self.env["hr.contract"].search(
                [
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                    ("employee_id", "=", record.id),
                ]
            )
            contracts.write({"active": active})
            if record.user_id:
                record.user_id.write({"active": record.active})
            if not active or not record.user_id:
                record.partner_id.write({"active": record.active})

    @api.multi
    def action_open_related_partner(self):
        action = self.env.ref("cb_hr_views.action_open_related_partner")
        result = action.read()[0]
        result["views"] = [(False, "form")]
        result["res_id"] = self.partner_id.id
        return result

    @api.multi
    def _compute_show_leaves(self):
        for employee in self:
            employee.show_leaves = employee.show_info

    @api.multi
    def _compute_show_info(self):
        is_manager = self.env.user.has_group("hr.group_hr_manager")
        is_officer = self.env.user.has_group("hr.group_hr_user")
        for employee in self:
            employee.show_info = (
                (is_officer and employee.parent_id.user_id.id == self.env.uid)
                or is_manager
                or employee.user_id.id == self.env.uid
            )

    @api.multi
    def _compute_is_manager(self):
        managers = self.env["hr.department"].search([]).mapped("manager_id")
        for record in self:
            record.manager = record.id in managers.ids

    @api.constrains("partner_id")
    def _check_practitioner(self):
        for record in self:
            if not record.partner_id.is_practitioner:
                raise ValidationError(_("All employees must be practitioners"))


class HrEmployeeCalendar(models.Model):
    _inherit = "hr.employee.calendar"
    _order = "date_end desc"
