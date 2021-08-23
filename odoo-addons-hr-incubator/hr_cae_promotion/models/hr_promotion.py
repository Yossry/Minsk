# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Promotion(models.Model):
    _name = "hr.promotion"
    _description = "Promotion"
    _order = "date_start,state"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("recruiting", "Recruiting"),
            ("active", "Active"),
            ("ended", "Ended"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="draft",
    )
    date_start = fields.Date(string="Start Date")
    user_id = fields.Many2one(
        comodel_name="res.users", string="Recruitment Responsible"
    )
    hr_responsible_id = fields.Many2one(
        comodel_name="res.users", string="HR Responsible"
    )
    employee_ids = fields.One2many(
        comodel_name="hr.employee",
        inverse_name="promotion_id",
        string="Employees",
    )
    applicant_ids = fields.One2many(
        comodel_name="hr.applicant",
        inverse_name="promotion_id",
        string="Applicants",
        domain=[("emp_id", "=", False)],
    )
    spots_regime = fields.Selection(
        [("limited", "Limited"), ("unlimited", "Unlimited")],
        "Regime",
        required=True,
        default="limited",
    )
    spots_max = fields.Integer(string="Maximum Spots", copy=False)
    spots_taken = fields.Integer(
        compute="_compute_spots_taken", string="Spots Taken", stre=True
    )
    spots_available = fields.Integer(
        compute="_compute_spots_available",
        string="Spots Available",
        store=True,
    )
    no_of_applicants = fields.Integer(
        compute="_compute_no_of_applicants",
        string="Number of Applicants",
        store=True,
    )
    attachment_number = fields.Integer(
        compute="_compute_attachment_number", string="Number of Attachments"
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        string="Attachments",
        domain=[("res_model", "=", "hr.promotion")],
    )

    @api.depends("employee_ids.active", "employee_ids.promotion_id")
    def _compute_spots_taken(self):
        for promotion in self:
            employees = self.env["hr.employee"].search(
                [("active", "=", True), ("promotion_id", "=", promotion.id)]
            )
            promotion.spots_taken = len(employees)

    @api.depends("spots_max", "spots_taken")
    def _compute_spots_available(self):
        for promotion in self:
            promotion.spots_available = (
                promotion.spots_max - promotion.spots_taken
            )

    @api.depends("applicant_ids.active", "applicant_ids.promotion_id")
    def _compute_no_of_applicants(self):
        for promotion in self:
            applicants = self.env["hr.applicant"].search(
                [("active", "=", True), ("promotion_id", "=", promotion.id)]
            )
            promotion.no_of_applicants = len(applicants)

    @api.multi
    @api.constrains("spots_regime", "spots_available")
    def _constrain_spots_available(self):
        for promotion in self:
            if (
                promotion.spots_regime == "limited"
                and promotion.spots_available < 0
            ):
                raise ValidationError(
                    _("Not enough spots available in this promotion.")
                )

    @api.multi
    def _compute_attachment_number(self):
        read_group_res = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hr.promotion"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        attach_data = {
            res["res_id"]: res["res_id_count"] for res in read_group_res
        }
        for promotion in self:
            promotion.attachment_number = attach_data.get(promotion.id, 0)

    @api.multi
    def action_get_attachment_tree_view(self):
        self.ensure_one()
        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.read()[0]
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            ["&", ("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        return action
