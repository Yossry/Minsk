import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ContractGroup(models.Model):
    _name = "hr.contract.group"
    _description = "Contract Group"
    _order = "amendment_index"

    contract_ids = fields.One2many(
        comodel_name="hr.contract",
        inverse_name="contract_group_id",
        string="Contracts",
    )

    def get_initial(self):
        return self.contract_ids.search(
            [("contract_group_id", "=", self.id)], limit=1
        )

    def get_parent(self, amendment_index):
        return self.contract_ids.search(
            [
                ("contract_group_id", "=", self.id),
                ("amendment_index", "<", amendment_index),
            ],
            order="amendment_index desc",
            limit=1,
        )

    def get_child(self, amendment_index):
        return self.contract_ids.search(
            [
                ("contract_group_id", "=", self.id),
                ("amendment_index", ">", amendment_index),
            ],
            limit=1,
        )

    def get_latest(self):
        return self.contract_ids.search(
            [("contract_group_id", "=", self.id)],
            order="amendment_index desc",
            limit=1,
        )

    def has_termination_contract(self):
        return bool(
            self.contract_ids.search(
                [
                    ("contract_group_id", "=", self.id),
                    ("echelon", "=", "termination"),
                ]
            )
        )


class ContractType(models.Model):

    _inherit = "hr.contract.type"

    echelon = fields.Selection(
        [
            ("main", "Main"),
            ("amendment", "Amendment"),
            ("termination", "Termination"),
        ],
        string="Echelon",
    )
    max_usage = fields.Integer(string="Maximum Usage", default=False)


class ContractTag(models.Model):

    _name = "hr.contract.tag"
    _description = "Contract Tag"

    name = fields.Char()


class Contract(models.Model):
    _inherit = "hr.contract"

    @api.model
    def _get_default_type_id(self):
        return self.env["hr.contract.type"].search([("name", "=", "Support")])

    name = fields.Char(compute="_compute_name")
    state = fields.Selection(
        [
            ("draft", "Reception"),
            ("support", "Support"),
            ("social_affairs", "Social Affairs"),
            ("open", "Running"),
            ("pending", "To Renew"),
            ("close", "Expired"),
            ("termination", "Terminated"),
            ("cancel", "Cancelled"),
        ],
        copy=False,
    )
    employee_id = fields.Many2one(required=True)
    echelon = fields.Selection(
        [
            ("main", "Main"),
            ("amendment", "Amendment"),
            ("termination", "Termination"),
        ],
        default="main",
        string="Contract Type Echelon",
        readonly=True,
        copy=False,
    )  # Todo: add translation "Échelon du Type de Contrat"
    type_id = fields.Many2one(
        string="Contract Type",
        domain="[('echelon', '=', echelon)]",
        default=_get_default_type_id,
        copy=False,
    )  # Todo: rename translation from "Catégorie de l'employé" to "Type de Contrat"
    type_count = fields.Integer(
        string="Contract Type Count", compute="_compute_type_count"
    )
    state_admin = fields.Text(string="Administrative state", copy=False)
    reason = fields.Char(string="Reason for recourse to contract", copy=False)
    tag_ids = fields.Many2many(comodel_name="hr.contract.tag", string="Tags")

    duration = fields.Integer(string="Duration", default=6)
    date_initial_start = fields.Date(
        string="Initial Starting Date",
        help="Start date of the initial contract.",
        related="parent_contract_id.date_start",
    )
    date_signature = fields.Date(
        string="Signature Date",
        help="Signature date of the contract.",
        copy=False,
    )
    date_mailing = fields.Date(
        string="Mailing Date", help="Mailing date of the contract.", copy=False
    )

    wage = fields.Monetary(
        string="Wage",
        digits=(16, 2),
        required=True,
        track_visibility="onchange",
        help="Employee's monthly gross wage.",
        compute="_compute_wage",
    )
    hours = fields.Float(string="Working Hours", required=True)
    hourly_wage = fields.Monetary(string="Hourly Wage", required=True)
    turnover_minimum = fields.Monetary(string="Minimum Turn-Over")

    amendment_index = fields.Integer(
        string="Amendment Index",
        help="'O' for main contract, '1' for it's first amendment, etc.",
        default=0,
        required=True,
        readonly=True,
    )
    contract_group_id = fields.Many2one(
        comodel_name="hr.contract.group", string="Contract Group"
    )
    contract_ids = fields.One2many(
        comodel_name="hr.contract", related="contract_group_id.contract_ids"
    )
    initial_contract_id = fields.Many2one(
        comodel_name="hr.contract",
        string="Initial Contract",
        readonly=True,
        compute="_compute_initial",
    )
    parent_contract_id = fields.Many2one(
        comodel_name="hr.contract",
        string="Previous Contract",
        ondelete="cascade",  # Deletion of the parent deletes the amendment
        readonly=True,
        compute="_compute_parent",
    )
    child_contract_id = fields.Many2one(
        comodel_name="hr.contract",
        string="Next Contract",
        readonly=True,
        compute="_compute_child",
    )
    latest_contract_id = fields.Many2one(
        comodel_name="hr.contract",
        string="Latest Contract",
        readonly=True,
        compute="_compute_latest",
    )
    has_termination_contract = fields.Boolean(
        string="Has Termination Contract",
        readonly=True,
        compute="_compute_has_termination_contract",
    )

    notes = fields.Text(copy=False)

    attachment_number = fields.Integer(
        compute="_compute_attachment_number", string="Number of Attachments"
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        string="Attachments",
        domain=[("res_model", "=", "hc.contract")],
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.contract_group_id:
            contract_group = self.env["hr.contract.group"].create({})
            res.contract_group_id = contract_group
        if res.amendment_index == 0:
            res._compute_initial()
        return res

    # Alternative for onchange (see below) such that it works on every write
    @api.multi
    def write(self, vals):
        res = super(Contract, self).write(vals)
        for contract in self:
            if (
                bool(vals.get("state"))
                and contract.echelon == "termination"
                and contract.state == "open"
            ):
                other_contracts = contract.contract_ids - contract
                other_contracts.write({"state": "termination"})
        return res

    # @api.onchange("state")
    # def onchange_state(self):
    #     if self.echelon == "termination" and self.state == "open":
    #         other_contracts = self.contract_ids - self._origin
    #         other_contracts.write({"state": "termination"})

    @api.multi
    @api.depends("employee_id", "initial_contract_id", "type_id")
    def _compute_name(self):
        for contract in self:
            contract.name = "/".join(
                filter(
                    None,
                    [
                        (contract.employee_id.name or ""),
                        (
                            contract.initial_contract_id.type_id.name
                            if contract.amendment_index > 0
                            else ""
                        ),
                        (
                            str(contract.amendment_index)
                            if contract.amendment_index > 0
                            else ""
                        ),
                        (contract.type_id.name or ""),
                    ],
                )
            )

    @api.multi
    @api.depends("contract_ids", "type_id")
    def _compute_type_count(self):
        for contract in self:
            type_count = 0
            for c in contract.contract_ids:
                if c.type_id == contract.type_id:
                    type_count += 1
            contract.type_count = type_count

    @api.multi
    @api.depends("hours", "hourly_wage")
    def _compute_wage(self):
        for contract in self:
            contract.wage = contract.hours * contract.hourly_wage

    def _compute_initial(self):
        for contract in self:
            contract.initial_contract_id = (
                contract.contract_group_id.get_initial()
            )

    def _compute_parent(self):
        for contract in self:
            contract.parent_contract_id = contract.contract_group_id.get_parent(
                contract.amendment_index
            )

    def _compute_child(self):
        for contract in self:
            contract.child_contract_id = contract.contract_group_id.get_child(
                self.amendment_index
            )

    def _compute_latest(self):
        for contract in self:
            contract.latest_contract_id = (
                contract.contract_group_id.get_latest()
            )

    def _compute_has_termination_contract(self):
        for contract in self:
            contract.has_termination_contract = (
                contract.contract_group_id.has_termination_contract()
            )

    @api.multi
    def _compute_attachment_number(self):
        read_group_res = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hr.contract"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        attach_data = {
            res["res_id"]: res["res_id_count"] for res in read_group_res
        }
        for contract in self:
            contract.attachment_number = attach_data.get(contract.id, 0)

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

    @api.onchange("date_start", "duration")
    def onchange_date_start_duration(self):
        if not self.duration:
            self.date_end = False
        if self.date_start and self.duration:
            self.date_end = self.date_start + relativedelta(
                months=self.duration
            )

    @api.onchange("date_end")
    def onchange_date_end(self):
        if not self.date_end:
            self.duration = False
        if self.date_start and self.date_end:
            rd = relativedelta(self.date_end, self.date_start)
            self.duration = rd.months + rd.years * 12

    @api.onchange("employee_id")
    def onchange_employee_id(self):
        if self.employee_id.turnover_minimum:
            self.turnover_minimum = self.employee_id.turnover_minimum
        if self.employee_id.date_start:
            self.date_start = self.employee_id.date_start

    #  Note: this check must run both when creating a new amendment
    #  and when changing the type_id of an amendment
    @api.multi
    @api.constrains("type_count", "type_id")
    def check_type_count(self):
        for contract in self:
            if (
                contract.type_id.max_usage
                and contract.type_count > contract.type_id.max_usage
            ):
                raise ValidationError(
                    _(
                        "The maximum amount of %s contracts "
                        "of type '%s' has been reached"
                        % (contract.type_id.max_usage, contract.type_id.name)
                    )
                )

    def create_amendment(self, type_id):
        self.ensure_one()
        return self._create_contract("amendment", type_id)

    def create_termination(self):
        self.ensure_one()
        type_id = self.env.ref("hr_cae_contract.hr_contract_type_termination")
        return self._create_contract("termination", type_id)

    def _create_contract(self, echelon, type_id):
        self.ensure_one()
        if self.has_termination_contract:
            raise ValidationError(
                _("This contract group already has a termination contract ")
            )
        if not type_id:
            type_id = self.env["hr.contract.type"].search(
                [("echelon", "=", echelon)], limit=1
            )

        _logger.info(
            "Creating Contract of echelon %s and type %s."
            % (echelon, type_id.name)
        )

        latest_contract_id = self.latest_contract_id
        contract = latest_contract_id.copy(
            {
                "state": "draft",
                "echelon": echelon,
                "type_id": type_id.id,
                "duration": False,
                "date_end": False,
                "amendment_index": latest_contract_id.amendment_index + 1,
            }
        )
        contract.check_type_count()

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.contract",
            "view_mode": "form",
            "res_id": contract.id,
            "target": "current",
            "context": {"form_view_initial_mode": "edit"},
        }
