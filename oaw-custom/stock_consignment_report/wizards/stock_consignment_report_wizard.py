# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class StockConsignmentReportWizard(models.TransientModel):
    _name = "stock.consignment.report.wizard"
    _description = "Stock Consignment Report Wizard"

    partner_id = fields.Many2one(
        comodel_name="res.partner", required=True, string="Partner"
    )
    threshold_date = fields.Date(
        required=True,
        string="Threshold Date",
        default=fields.Date.to_string(datetime.now() - relativedelta(days=15)),
    )

    @api.multi
    def action_export_xlsx(self):
        self.ensure_one()
        model = self.env["stock.consignment.report"]
        report = model.create(self._prepare_report_xlsx())
        return report.print_report()

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            "filter_partner_id": self.partner_id.id,
            "threshold_date": self.threshold_date,
        }
