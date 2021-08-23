# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    paid_date = fields.Date(
        store=True, compute="_compute_paid_date_info", string="Paid Date"
    )
    paid_date_currency_rate = fields.Float(
        store=True,
        compute="_compute_paid_date_info",
        string="Paid Date Currency Rate",
        digits=(12, 6),
    )

    @api.multi
    @api.depends("state")
    def _compute_paid_date_info(self):
        for account_invoice in self:
            if account_invoice.state == "paid":
                paid_date = False
                for payment_id in account_invoice.payment_ids:
                    if not paid_date or (
                        paid_date and payment_id.payment_date > paid_date
                    ):
                        paid_date = payment_id.payment_date
                if paid_date:
                    account_invoice.paid_date = paid_date
                    if (
                        account_invoice.currency_id
                        == account_invoice.company_id.currency_id
                    ):
                        rate = 1.0
                    else:
                        rate = self.env["res.currency"]._get_conversion_rate(
                            account_invoice.currency_id,
                            account_invoice.company_id.currency_id,
                            account_invoice.company_id,
                            paid_date,
                        )
                    account_invoice.paid_date_currency_rate = 1 / rate
        return
