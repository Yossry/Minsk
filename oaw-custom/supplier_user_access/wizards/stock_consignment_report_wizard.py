# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockConsignmentReportWizard(models.TransientModel):
    _inherit = "stock.consignment.report.wizard"

    def _prepare_report_xlsx(self):
        data = super(StockConsignmentReportWizard, self)._prepare_report_xlsx()
        if self.env.user.has_group("supplier_user_access.group_supplier"):
            data["filter_partner_id"] = self.env.user.partner_id.id
        return data
