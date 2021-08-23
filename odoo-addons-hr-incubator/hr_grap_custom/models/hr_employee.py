# Copyright 2019 Coop IT Easy SCRL fs
# Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    # Columns Section
    mutual_insurance_state = fields.Selection(
        [
            ("affiliated", "Affiliated"),
            ("exempted", "Exempted"),
            ("dontknowyet", "Don't know yet"),
        ],
        string="State for Mutual Insurance",
        default="dontknowyet",
        required=True,
        help="Help to know if this employee should have Mutual",
    )

    mutual_insurance_proof_received = fields.Boolean(
        string="Proof received", default=False
    )
