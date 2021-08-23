# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockConsignmentReport(models.TransientModel):
    _inherit = "stock.consignment.report"

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        model = self.env["stock.consignment.report.quant"]
        self._create_section_records()
        sections = self.env["stock.consignment.report.section"].search(
            [("report_id", "=", self.id)]
        )
        for section in sections:
            self._inject_quant_values(section)
            self._update_age(model, section)
            if section.code == 1:
                self._update_invoice_info(section.id, section.code)
                if self.env.user.has_group("supplier_user_access.group_supplier"):
                    self._update_supplier_remark(model, section.id)
            elif section.code == 2:
                self._update_reservation(model, section.id)
            elif section.code == 3:
                self._delete_supplier_loc_quant(model, section.id)
                self._update_remark(model, section.id, "supplier")
            else:
                self._update_remark(model, section.id, "internal")
        self.refresh()

    # Update the remark field in the section in case the quant is sold to
    # supplier's customer
    def _update_supplier_remark(self, model, section_id):
        quants = model.search([("section_id", "=", section_id)])
        for quant in quants:
            order_line = (
                self.env["sale.order.line"]
                .sudo()
                .search(
                    [
                        ("quant_id", "=", quant.quant_id.id),
                        ("state", "not in", ("draft", "sent", "cancel")),
                        ("stock_owner_id", "=", self.env.user.partner_id.id),
                    ]
                )
            )
            for line in order_line:
                if (
                    line.order_id.partner_id.related_partner
                    and line.order_id.partner_id.related_partner
                    == self.env.user.partner_id
                ):
                    quant.remark = line.order_id.partner_id.name_get()[0][1]
