# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    currency_id = fields.Many2one(
        string="Currency", related="company_id.currency_id", readonly=True
    )
    title = fields.Many2one("res.partner.title")
    country_department_of_birth_id = fields.Many2one(
        "res.country.department",
        string="Department (France) of Birth",
        required=False,
    )
    country_other_ids = fields.Many2many(
        "res.country", string="Other Nationalities", required=False
    )
    date_start = fields.Date(
        string="Date of Entry", default=fields.Date.today(), required=False
    )
    date_end = fields.Date(string="Date of Obsolescence")
    origin_status_id = fields.Many2one(
        "hr.origin.status", string="Origin Status", required=False
    )
    origin_status_details_id = fields.Many2one(
        "hr.origin.status.details",
        string="Origin Status Details",
        domain="[('origin_status_id', '=', origin_status_id)]",
        required=False,
    )
    certificate_id = fields.Many2one(
        "hr.recruitment.degree", string="Certificate", required=False
    )
    certificate_date = fields.Date(
        string="Certificate Date",
        help="Certificate Delivery Date",
        required=False,
    )
    professional_experience = fields.Text(
        string="Professional Experience", required=False
    )
    bank_account_payment_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account Number for Payment",
        required=False,
        domain="[('partner_id', '=', address_home_id)]",
        help="Employee bank salary account",
    )  # TODO: check that this one is actually used in logic
    turnover_minimum = fields.Monetary(string="Minimum Turn-Over")
    coop_role_id = fields.Many2one(
        "hr.coop.role", string="Role in the cooperative", required=False
    )
    social_insurance_id = fields.Many2one(
        "hr.social.insurance", string="Social Insurance", required=False
    )
    mutual_insurance_id = fields.Many2one(
        "hr.mutual.insurance", string="Mutual Insurance", required=False
    )
    mutual_insurance_level_id = fields.Many2one(
        "hr.mutual.insurance.level",
        string="Mutual Insurance Level",
        required=False,
    )
    mutual_insurance_date_start = fields.Date(
        string="Start Date of Mutual Insurance", required=False
    )
    mutual_insurance_date_end = fields.Date(
        string="End Date of Mutual Insurance", required=False
    )
    mutual_insurance_date_exemption = fields.Date(
        string="Exemption Date Mutual Insurance", required=False
    )
    medic_dispense_date = fields.Date(
        string="Date of Medical Dispense", required=False
    )
    transport_mode_id = fields.Many2one(
        "hr.transport.mode", string="Transport Mode", required=False
    )
    invalidity_rate = fields.Float(
        string="Invalidity Rate", required=False, default=0
    )  # use percentage widget
    job_other_companies = fields.Text(string="Other Employers", required=False)
    job_other_hours = fields.Float(
        string="Cumulative Other Monthly Working Hours", required=False
    )
    job_retirement = fields.Boolean(
        string="Combining Job and Retirement", required=False
    )
    job_adaptations = fields.Text(string="Job Adaptations", required=False)
    children = fields.Integer(string="Number of Children", required=False)
    valid_mandate_id = fields.Many2one(
        related="user_id.partner_id.valid_mandate_id"
    )
    siren = fields.Char(
        "SIREN Company Code", required=False
    )  # todo: link from partner
    ape = fields.Char("APE Profession Code")  # todo: link from partner
    # todo: install l10n_fr_naf_ape when migrated module for easy lookup
    professional_liability_ids = fields.Many2many(
        comodel_name="hr.professional.liability",
        string="Professional Liability",
        required=False,
    )
    professional_liability_insurance_policy_ref = fields.Text(
        string="Professional Liability Insurance Policy Reference",
        required=False,
    )
    vehicle_insurance = fields.Text(string="Vehicle Insurance", required=False)
    office = fields.Text(string="Office", required=False)
    equipment = fields.Text(string="Equipment", required=False)
    sector_ids = fields.Many2many(
        comodel_name="hr.sector", string="Sector", required=False
    )
    adult_dependents = fields.Integer(
        string="Number of Adult Dependents", required=False
    )
    social_worker = fields.Text(string="Social Worker", required=False)
    contribution_date_start = fields.Date(
        string="Start Date of Contributions", required=False
    )
    # contribution_arrangements = fields.Selection(
    #     related="partner_id.contribution_arrangements"
    # ) # Todo: field will be available from Scopa in partner_id
    # fixme should be Many2One
    contribution_exemption_ids = fields.One2many(
        comodel_name="hr.contribution.exemption",
        inverse_name="employee_id",
        string="Contribution Exemptions",
        required=False,
    )

    _sql_constraints = [
        (
            "check_invalidity_rate",
            "CHECK(invalidity_rate >= 0 AND invalidity_rate <= 100)",
            "The percentage of an invalidity_rate should be between 0 and 100.",
        ),
        (
            "check_job_other_hours",
            "CHECK(job_other_hours >= 0)",
            "The cumulative other working hours should greater then or equal to 0.",
        ),
        (
            "check_adult_dependents",
            "CHECK(adult_dependents >= 0)",
            "The number of Adult Dependents should greater then or equal to 0.",
        ),
    ]

    @api.constrains("date_start", "date_end")
    def _constrain_date(self):
        for employee in self:
            if (
                employee.date_start
                and employee.date_end
                and employee.date_start > employee.date_end
            ):
                raise ValidationError(
                    _("The entry date must be before obsolescence date")
                )

    @api.constrains("mutual_insurance_date_start", "mutual_insurance_date_end")
    def _constrain_mutual_insurance_date(self):
        for employee in self:
            if (
                employee.mutual_insurance_date_start
                and employee.mutual_insurance_date_end
                and employee.mutual_insurance_date_start
                > employee.mutual_insurance_date_end
            ):
                raise ValidationError(
                    _(
                        "The start date of mutual insurance must be before"
                        " the end date"
                    )
                )
