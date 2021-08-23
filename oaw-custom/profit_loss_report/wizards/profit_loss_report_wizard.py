# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

report_filters = ["product_id", "lot_id", "partner_id", "supplier_id", "reference"]


class ProfitLossReportWizard(models.TransientModel):
    _name = "profit.loss.report.wizard"
    _description = "Profit & Loss Report Wizard"

    from_date = fields.Date(
        required=True,
        string="From Date",
        default=fields.Date.to_string(datetime.now().replace(day=1)),
    )
    to_date = fields.Date(
        required=True, string="To Date", default=fields.Date.context_today
    )
    product_id = fields.Many2many("product.product", string="Product")
    lot_id = fields.Many2many("stock.production.lot", string="Case No.")
    partner_id = fields.Many2many(
        "res.partner", "profit_loss_report_partner_id_filter", string="Customer"
    )
    supplier_id = fields.Many2many(
        "res.partner", "profit_loss_report_supplier_id_filter", string="Supplier"
    )
    reference = fields.Char(string="Vendor Reference")

    def _inject_out_invoice_data(self, from_date, to_date):
        query = """
        INSERT INTO
            profit_loss_report (
                create_uid,
                create_date,
                product_id,
                categ_id,
                categ_name,
                lot_id,
                date_order,
                user_id,
                sale_order_id,
                invoice_id,
                list_price,
                net_price,
                net_price_currency_id,
                partner_id,
                partner_ref,
                sale_order_note,
                out_move_line_id,
                out_move_date,
                in_move_line_id,
                in_move_date,
                in_move_quant_owner_id,
                purchase_order_id,
                supplier_id,
                supplier_ref,
                purchase_currency_id,
                purchase_currency_price,
                purchase_invoice_id,
                purchase_invoice_line_id,
                reference,
                customer_invoice_type,
                supplier_invoice_type
            )
        WITH
            outgoing_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sml.id,
                    sq.lot_id,
                    sml.date
                FROM
                    stock_move_line sml
                JOIN
                    stock_location sl ON sml.location_dest_id = sl.id
                JOIN
                    stock_quant sq ON sml.quant_id = sq.id
                JOIN
                    stock_move sm ON sm.id = sml.move_id
                WHERE
                    sl.usage = 'customer' AND
                    sml.state = 'done' AND
                    sq.quantity > 0 AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sml.date desc
            ),
            incoming_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sml.id,
                    sq.lot_id,
                    sml.date,
                    sq.owner_id
                FROM
                    stock_move_line sml
                JOIN
                    stock_location sl ON sml.location_id = sl.id
                JOIN
                    stock_quant sq ON sml.quant_id = sq.id
                JOIN
                    stock_move sm ON sm.id = sml.move_id
                WHERE
                    sl.usage = 'supplier' AND
                    sml.state = 'done' AND
                    sq.quantity > 0 AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sml.date
            ),
            purchase_data AS (
                SELECT DISTINCT ON (pol.lot_id)
                    po.id AS purchase_id,
                    po.partner_id,
                    rp.ref,
                    po.currency_id,
                    pol.id AS purchase_line_id,
                    pol.price_unit,
                    pol.lot_id
                FROM
                    purchase_order_line pol
                JOIN
                    purchase_order po ON pol.order_id = po.id
                JOIN
                    res_partner rp ON po.partner_id = rp.id
                WHERE
                    pol.company_id = %s
                ORDER BY
                    pol.lot_id,
                    po.date_order desc
            ),
            purchase_invoice_data AS (
                SELECT
                    ail.id as purchase_invoice_line_id,
                    ail.purchase_line_id,
                    ai.id AS supplier_invoice_id,
                    ai.reference,
                    ai.type AS supplier_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('in_invoice', 'in_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.purchase_line_id,
                    ai.date_invoice
            )
        SELECT
            %s AS create_uid,
            NOW() AS create_date,
            pp.id,
            pc.id,
            pc.name,
            ail.lot_id,
            so.date_order,
            ai.user_id,
            so.id,
            ai.id,
            pt.list_price,
            ail.price_subtotal,
            ai.currency_id,
            so.partner_id,
            rp.ref,
            so.note,
            om.id,
            om.date,
            im.id,
            im.date,
            im.owner_id,
            pd.purchase_id,
            pd.partner_id,
            pd.ref,
            pd.currency_id,
            pd.price_unit,
            pid.supplier_invoice_id,
            pid.purchase_invoice_line_id,
            pid.reference,
            ai.type,
            pid.supplier_invoice_type
        FROM
            account_invoice_line ail
        JOIN
            account_invoice ai ON ail.invoice_id = ai.id
        JOIN
            product_product pp ON ail.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            product_category pc ON pt.categ_id = pc.id
        JOIN
            res_partner rp ON ai.partner_id = rp.id
        LEFT JOIN
            sale_order_line_invoice_rel soliv ON soliv.invoice_line_id = ail.id
        LEFT JOIN
            sale_order_line sol ON sol.id = soliv.order_line_id
        LEFT JOIN
            sale_order so ON so.id = sol.order_id
        LEFT JOIN
            outgoing_moves om ON ail.lot_id = om.lot_id
        LEFT JOIN
            incoming_moves im ON ail.lot_id = im.lot_id
        LEFT JOIN
            purchase_data pd ON ail.lot_id = pd.lot_id
        LEFT JOIN
            purchase_invoice_data pid ON
                pd.purchase_line_id = pid.purchase_line_id
        WHERE
            ai.type in ('out_invoice', 'out_refund') AND
            (ai.type, pid.supplier_invoice_type) NOT IN (('out_refund',
            'in_refund')) AND
            ai.state in ('open', 'paid') AND
            ai.date_invoice >= %s AND
            ai.date_invoice <= %s AND
            ail.company_id = %s
        """
        company_id = self.env.user.company_id.id
        params = (
            company_id,
            company_id,
            company_id,
            company_id,
            self.env.uid,
            from_date,
            to_date,
            company_id,
        )
        self.env.cr.execute(query, params)

    def _inject_purchase_data(self, from_date, to_date):
        query = """
        INSERT INTO
            profit_loss_report (
                create_uid,
                create_date,
                product_id,
                categ_id,
                categ_name,
                lot_id,
                date_order,
                user_id,
                sale_order_id,
                invoice_id,
                list_price,
                net_price,
                net_price_currency_id,
                partner_id,
                partner_ref,
                sale_order_note,
                out_move_line_id,
                out_move_date,
                in_move_line_id,
                in_move_date,
                in_move_quant_owner_id,
                purchase_order_id,
                supplier_id,
                supplier_ref,
                purchase_currency_id,
                purchase_currency_price,
                purchase_invoice_id,
                purchase_invoice_line_id,
                reference,
                customer_invoice_type,
                supplier_invoice_type
            )
        WITH
            outgoing_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sml.id,
                    sq.lot_id,
                    sml.date
                FROM
                    stock_move_line sml
                JOIN
                    stock_location sl ON sml.location_dest_id = sl.id
                JOIN
                    stock_quant sq ON sml.quant_id = sq.id
                JOIN
                    stock_move sm ON sm.id = sml.move_id
                WHERE
                    sl.usage = 'customer' AND
                    sml.state = 'done' AND
                    sq.quantity > 0 AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sml.date desc
            ),
            incoming_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sml.id,
                    sq.lot_id,
                    sml.date,
                    sq.owner_id
                FROM
                    stock_move_line sml
                JOIN
                    stock_location sl ON sml.location_id = sl.id
                JOIN
                    stock_quant sq ON sml.quant_id = sq.id
                JOIN
                    stock_move sm ON sm.id = sml.move_id
                WHERE
                    sl.usage = 'supplier' AND
                    sml.state = 'done' AND
                    sq.quantity > 0 AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sml.date
            ),
            purchase_invoice_data AS (
                SELECT
                    ail.lot_id,
                    ail.purchase_line_id,
                    ail.id AS purchase_invoice_line_id,
                    ai.id AS supplier_invoice_id,
                    ai.reference,
                    ai.type AS supplier_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('in_invoice', 'in_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.purchase_line_id,
                    supplier_invoice_type,
                    ai.date_invoice
            ),
            customer_invoice_data AS (
                SELECT
                    ail.lot_id,
                    ai.id AS customer_invoice_id,
                    ai.user_id,
                    ail.price_subtotal,
                    ai.currency_id,
                    ai.type AS customer_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('out_invoice', 'out_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.lot_id,
                    ai.date_invoice
            )
        SELECT
            %s AS create_uid,
            NOW() AS create_date,
            pp.id,
            pc.id,
            pc.name,
            im.lot_id,
            so.date_order,
            cid.user_id,
            so.id,
            cid.customer_invoice_id,
            pt.list_price,
            cid.price_subtotal,
            cid.currency_id,
            so.partner_id,
            rp.ref,
            so.note,
            om.id,
            om.date,
            im.id,
            im.date,
            im.owner_id,
            po.id,
            po.partner_id,
            rp.ref,
            po.currency_id,
            pol.price_unit,
            COALESCE(pid.supplier_invoice_id, pid2.supplier_invoice_id),
            COALESCE(pid.purchase_invoice_line_id, pid2.purchase_invoice_line_id),
            COALESCE(pid.reference, pid2.reference),
            cid.customer_invoice_type,
            COALESCE(NULLIF(pid.supplier_invoice_type, ''), pid2.supplier_invoice_type)
        FROM
            purchase_order_line pol
        JOIN
            purchase_order po ON pol.order_id = po.id
        JOIN
            product_product pp ON pol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            product_category pc ON pt.categ_id = pc.id
        JOIN
            res_partner rp ON pol.partner_id = rp.id
        LEFT JOIN
            purchase_invoice_data pid ON
                pol.lot_id = pid.lot_id
        LEFT JOIN
            purchase_invoice_data pid2 ON
                pol.id = pid2.purchase_line_id
        LEFT JOIN
            sale_order_line sol ON pol.lot_id = sol.lot_id
        LEFT JOIN
            sale_order so ON sol.order_id = so.id
        LEFT JOIN
            customer_invoice_data cid ON
                pol.lot_id = cid.lot_id
        LEFT JOIN
            outgoing_moves om ON pol.lot_id = om.lot_id
        LEFT JOIN
            incoming_moves im ON pol.lot_id = im.lot_id
        WHERE
            po.state not in ('draft', 'sent', 'cancel') AND
            po.id not in (
                SELECT DISTINCT purchase_order_id
                FROM profit_loss_report
            ) AND
            po.date_order >= %s AND
            po.date_order <= (TIMESTAMP %s + INTERVAL '1 DAY') AND
            po.company_id = %s
        """
        company_id = self.env.user.company_id.id
        params = (
            company_id,
            company_id,
            company_id,
            company_id,
            self.env.uid,
            from_date,
            to_date,
            company_id,
        )
        self.env.cr.execute(query, params)

    @api.multi
    def _update_records(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx["company_id"] = self.env.user.company_id.id
        recs = self.env["profit.loss.report"].search([])
        for rec in recs:
            # Get the period of the record
            if rec.in_move_date:
                rec.in_period_id = (
                    self.env["account.period"]
                    .with_context(ctx)
                    .find(rec.in_move_date)[:1]
                )

            # Define quant type
            if rec.in_move_quant_owner_id:
                if rec.in_move_quant_owner_id == self.env.user.company_id.partner_id:
                    rec.stock_type = "own"
                else:
                    rec.stock_type = "vci"

            # Handle the purchase price
            if rec.purchase_invoice_line_id:
                invoice_line = rec.purchase_invoice_line_id
                rec.purchase_currency_price = invoice_line.price_unit * (
                    1.0 - (invoice_line.discount or 0.0) / 100.0
                )
                rec.purchase_currency_id = invoice_line.invoice_id.currency_id
                if invoice_line.invoice_id.paid_date:
                    rec.exchange_rate = (
                        1 / invoice_line.invoice_id.paid_date_currency_rate
                    )
                else:
                    rec.exchange_rate = 1 / invoice_line.rate
            elif not rec.purchase_order_id and rec.stock_type == "vci":
                if rec.supplier_id:
                    rec.supplier_ref = rec.in_move_quant_owner_id.ref
                if rec.in_move_id:
                    rec.purchase_order_id = rec.in_move_id.purchase_line_id.order_id
                    rec.purchase_currency_id = rec.in_move_id.currency_id
                    rec.purchase_currency_price = rec.in_move_id.purchase_price_unit

            # Determine the purchase exchange rate
            if rec.stock_type == "vci":
                ctx["date"] = rec.out_move_date or rec.invoice_id.date_invoice
            elif not rec.in_move_date and rec.purchase_order_id:
                ctx["date"] = rec.purchase_order_id.date_order
            else:
                ctx["date"] = rec.in_move_date
            comp_currency_id = self.env.user.company_id.currency_id
            if not rec.exchange_rate:
                if rec.purchase_currency_id == comp_currency_id:
                    rec.exchange_rate = 1.0
                elif ctx["date"] and rec.purchase_currency_id:
                    rec.exchange_rate = (
                        self.env["res.currency"]
                        .with_context(ctx)
                        ._get_conversion_rate(
                            rec.purchase_currency_id,
                            comp_currency_id,
                            self.env.user.company_id,
                            ctx["date"],
                        )
                    )
            # Handle the net price
            net_price_exchange_rate = 1.0
            if rec.net_price_currency_id == comp_currency_id:
                net_price_exchange_rate = 1.0
            elif ctx["date"] and rec.net_price_currency_id:
                net_price_exchange_rate = (
                    self.env["res.currency"]
                    .with_context(ctx)
                    ._get_conversion_rate(
                        rec.net_price_currency_id,
                        comp_currency_id,
                        self.env.user.company_id,
                        ctx["date"],
                    )
                )
            base_net_price = rec.net_price * net_price_exchange_rate
            rec.purchase_base_price = rec.purchase_currency_price * rec.exchange_rate

            # Handle the display of multi-payments

            rec.supplier_payment_dates = ", ".join(
                [
                    fields.Date.to_string(d)
                    for d in rec.sudo().supplier_payment_ids.mapped("payment_date")
                ]
            )
            rec.supplier_payment_ref = ", ".join(
                rec.sudo().supplier_payment_ids.mapped("communication")
            )
            if rec.invoice_id.state == "paid":
                (
                    rec.customer_payment_reference,
                    rec.customer_payment_currency_rate,
                    rec.sale_base_price,
                ) = self._get_payment_information(
                    rec.sudo().customer_payment_ids, rec.net_price, rec.invoice_id
                )
                if rec.sale_base_price:
                    base_net_price = rec.sale_base_price

            # Calculate the base_profit
            if (
                rec.invoice_id
                and rec.invoice_id.state == "paid"
                and rec.purchase_invoice_id
                and rec.purchase_invoice_id.state == "paid"
            ):
                if rec.customer_invoice_type:
                    if rec.customer_invoice_type == "out_refund":
                        rec.base_profit = rec.purchase_base_price - base_net_price
                    elif rec.customer_invoice_type == "out_invoice":
                        if rec.supplier_invoice_type:
                            if rec.supplier_invoice_type == "in_invoice":
                                rec.base_profit = (
                                    base_net_price - rec.purchase_base_price
                                )
                            else:
                                rec.base_profit = 0
                elif rec.supplier_invoice_type:
                    rec.base_profit = 0
                else:
                    rec.base_profit = base_net_price - rec.purchase_base_price
                if rec.purchase_base_price:
                    rec.base_profit_percent = (
                        rec.base_profit / rec.purchase_base_price * 100
                    )
                else:
                    rec.base_profit_percent = 999.99

            # FIXME below 'if' block may be deprecated as necessary
            # Identify the state of the transaction
            if rec.purchase_invoice_id and rec.purchase_invoice_id.state == "paid":
                rec.supplier_payment_state = "done"
            else:
                rec.supplier_payment_state = "to_pay"
            if rec.out_move_id and rec.out_move_id.state == "done" and rec.invoice_id:
                if rec.invoice_id.state == "paid":
                    rec.sale_state = "done"
                elif rec.invoice_id.residual and rec.sudo().customer_payment_ids:
                    rec.sale_state = "balance"
                else:
                    rec.sale_state = "open"
            if rec.customer_invoice_type and rec.customer_invoice_type == "out_refund":
                rec.state = "out_refund"
            elif rec.customer_invoice_type and rec.customer_invoice_type == "in_refund":
                rec.state = "in_refund"
            elif rec.supplier_invoice_type and rec.supplier_invoice_type == "in_refund":
                rec.state = "in_refund"
            elif (
                rec.purchase_invoice_id
                and rec.purchase_invoice_id.state == "paid"
                and rec.invoice_id
                and rec.invoice_id.state == "paid"
            ):
                rec.state = "sale_purch_done"
            elif rec.purchase_invoice_id and rec.purchase_invoice_id.state == "paid":
                rec.state = "purch_done"
            elif rec.invoice_id and rec.invoice_id.state == "paid":
                rec.state = "sale_done"

    def _get_utc_date(self, date_tz):
        tz = self.env.user.tz and pytz.timezone(self.env.user.tz) or pytz.utc
        date_string = datetime.strftime(date_tz, DEFAULT_SERVER_DATE_FORMAT)
        date_local = tz.localize(fields.Datetime.from_string(date_string), is_dst=None)
        return date_local.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _get_payment_information(self, payment_ids, net_price, invoice_id):
        payment_reference = ", ".join(payment_ids.mapped("communication"))
        payment_currency_rate = False
        sale_base_price = False
        if len(payment_ids) == 1:
            payment = payment_ids[0]
            payment_reference = payment.communication
            payment_currency_rate = invoice_id.paid_date_currency_rate
            sale_base_price = net_price / payment_currency_rate
        return payment_reference, payment_currency_rate, sale_base_price

    def _filter_records(self):
        filters = []
        for report_filter in report_filters:
            if self[report_filter]:
                if type(self[report_filter]) == str:
                    value = self[report_filter].strip()
                    filters.append(
                        "(%s NOT ILIKE '%%%s%%' OR %s IS NULL)"
                        % (report_filter, value, report_filter)
                    )
                else:
                    value = ",".join([str(id) for id in self[report_filter].ids])
                    filters.append(
                        "({} NOT IN ({}) OR {} IS NULL)".format(
                            report_filter, value, report_filter
                        )
                    )
        if filters:
            filter_sql = "DELETE FROM profit_loss_report WHERE %s" % (
                " OR ".join(filters)
            )
            self.env.cr.execute(filter_sql)

    @api.multi
    def _update_supplier_info(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx["company_id"] = self.env.user.company_id.id
        recs = self.env["profit.loss.report"].search(
            [
                ("in_move_quant_owner_id", "!=", False),
                ("purchase_invoice_line_id", "=", False),
                ("purchase_order_id", "=", False),
            ]
        )
        for rec in recs:
            if rec.in_move_quant_owner_id != self.env.user.company_id.partner_id:
                rec.supplier_id = rec.in_move_quant_owner_id

    @api.multi
    def action_generate_profit_loss_records(self):
        self.ensure_one()
        self.env.cr.execute("DELETE FROM profit_loss_report")
        self._inject_out_invoice_data(self.from_date, self.to_date)
        from_date = self._get_utc_date(self.from_date)
        to_date = self._get_utc_date(self.to_date)
        self._inject_purchase_data(from_date, to_date)
        self._update_supplier_info()
        self._filter_records()
        self._update_records()
        res = self.env.ref("profit_loss_report.profit_loss_report_action")
        return res.read()[0]

    @api.onchange("product_id")
    def onchange_product_id(self):
        ids = []
        for product in self.product_id:
            # Update case number domain filter
            lot_ids = self.env["stock.production.lot"].search(
                [("product_id", "=", product.id)]
            )
            ids += lot_ids.ids
        return (
            {"domain": {"lot_id": [("id", "in", ids)]}}
            if ids
            else {"domain": {"lot_id": []}}
        )
