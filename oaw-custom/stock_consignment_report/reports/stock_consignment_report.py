# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockConsignmentReport(models.TransientModel):
    _name = "stock.consignment.report"

    # Filters fields, used for data computation
    company_id = fields.Many2one(comodel_name="res.company")
    filter_partner_id = fields.Many2one(comodel_name="res.partner")
    threshold_date = fields.Date()
    current_date = fields.Date(default=fields.Date.context_today)
    # Data fields, used to browse report data
    section_ids = fields.One2many(
        comodel_name="stock.consignment.report.section", inverse_name="report_id"
    )
    quant_ids = fields.One2many(
        comodel_name="stock.consignment.report.quant", inverse_name="report_id"
    )


class StockConsignmentReportSection(models.TransientModel):
    _name = "stock.consignment.report.section"
    # _order = 'name ASC'

    report_id = fields.Many2one(
        comodel_name="stock.consignment.report", ondelete="cascade", index=True
    )
    quant_ids = fields.One2many(
        comodel_name="stock.consignment.report.quant", inverse_name="section_id"
    )

    # Data fields, used for report display
    code = fields.Integer()


class StockConsignmentReportQuant(models.TransientModel):
    _name = "stock.consignment.report.quant"

    report_id = fields.Many2one(
        comodel_name="stock.consignment.report", ondelete="cascade", index=True
    )
    section_id = fields.Many2one(
        comodel_name="stock.consignment.report.section", ondelete="cascade", index=True
    )

    # Data fields, used to keep link with real object
    quant_id = fields.Many2one("stock.quant", index=True)
    reservation_id = fields.Many2one("stock.move", index=True)
    sale_id = fields.Many2one("sale.order")
    lot_id = fields.Many2one("stock.production.lot", index=True)

    # Data fields, used for report display
    product_code = fields.Char()
    product_name = fields.Char()
    lot = fields.Char()
    currency = fields.Char()
    purchase_price = fields.Float(digits=(16, 2))
    status = fields.Char()
    remark = fields.Char()
    incoming_date = fields.Datetime()
    stock_days = fields.Integer()
    quant_last_updated = fields.Datetime()
    outgoing_date = fields.Datetime()


class StockConsignmentReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = "stock.consignment.report"

    @api.multi
    def print_report(self):
        self.ensure_one()
        self.compute_data_for_report()
        datas = {
            "ids": self.env.context.get("active_ids", []),
            "model": "stock.consignment.report",
            "form": self.read()[0],
        }
        return self.env.ref(
            "stock_consignment_report.stock_consignment_report_xlsx"
        ).report_action(self, data=datas)

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            "filter_partner_id": [(6, 0, self.filter_partner_id.id)],
            "threshold_date": self.threshold_date,
        }

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
            elif section.code == 2:
                self._update_reservation(model, section.id)
            elif section.code == 3:
                self._delete_supplier_loc_quant(model, section.id)
                self._update_remark(model, section.id, "supplier")
            else:
                self._update_remark(model, section.id, "internal")
        self.refresh()

    def _create_section_records(self):
        model = self.env["stock.consignment.report.section"]
        for i in [1, 2, 3, 4]:
            vals = {"report_id": self.id, "code": i}
            model.create(vals)

    def _inject_quant_values(self, section):
        query_inject_quant = ""
        if section.code == 1:
            query_inject_quant += """
WITH
    paid_lot AS (
        SELECT
            lot_id, COALESCE(inv_qty, 0.0) - COALESCE(ref_qty, 0.0) AS qty
        FROM (
            SELECT DISTINCT
                l.lot_id, normal.inv_qty, refund.ref_qty
            FROM
                account_invoice_line l
            INNER JOIN
                account_invoice i ON l.invoice_id = i.id
            LEFT JOIN (
                SELECT
                    lot_id, sum(quantity) AS inv_qty
                FROM
                    account_invoice_line l1
                INNER JOIN
                    account_invoice i1 ON l1.invoice_id = i1.id
                WHERE
                    i1.type = 'in_invoice'
                    AND i1.state = 'paid'
                GROUP BY
                    l1.lot_id
            ) normal ON l.lot_id = normal.lot_id
            LEFT JOIN (
                SELECT
                    lot_id, sum(quantity) AS ref_qty
                FROM
                    account_invoice_line l2
                INNER JOIN
                    account_invoice i2 ON l2.invoice_id = i2.id
                WHERE
                    i2.type = 'in_refund'
                    AND i2.state = 'paid'
                GROUP BY
                    l2.lot_id
            ) refund ON l.lot_id = refund.lot_id
            WHERE i.type = 'in_invoice'
        ) normref
        WHERE
            COALESCE(inv_qty, 0.0) - COALESCE(ref_qty, 0.0) > 0.0
    )
            """
        query_inject_quant += """
INSERT INTO
    stock_consignment_report_quant
    (
    report_id,
    section_id,
    create_uid,
    create_date,
    quant_id,
    reservation_id,
    sale_id,
    product_code,
    product_name,
    lot_id,
    lot,
    currency,
    purchase_price,
    status,
    incoming_date,
    quant_last_updated
    )
SELECT
    %s AS report_id,
    %s AS section_id,
    %s AS create_uid,
    NOW() AS create_date,
    q.id,
    q.reservation_id,
    q.sale_order_id,
    p.default_code,
    pt.name,
    l.id,
    l.name,
    c.name,
    q.purchase_price_unit,
    %s AS status,
    q.in_date,
    q.write_date
FROM
    stock_quant q
INNER JOIN
    product_product p ON q.product_id = p.id
INNER JOIN
    product_template pt ON pt.id = p.product_tmpl_id
INNER JOIN
    stock_production_lot l ON q.lot_id = l.id
INNER JOIN
    stock_location loc ON q.location_id = loc.id
        """
        if section.code != 4:
            query_inject_quant += """
INNER JOIN
    res_currency c ON q.currency_id = c.id
    """
        else:
            query_inject_quant += """
LEFT JOIN
    res_currency c ON q.currency_id = c.id
    """
        if section.code == 1:
            query_inject_quant += """
LEFT JOIN
    paid_lot pl ON q.lot_id = pl.lot_id
            """
        query_inject_quant += """
WHERE
    q.quantity > 0
    AND loc.usage = %s
    AND loc.return_location = %s
    AND q.owner_id = %s
            """
        if section.code in [1, 3]:
            query_inject_quant += """
    AND q.write_date >= %s
            """
        if section.code == 1:
            query_inject_quant += """
    AND pl.lot_id IS null
            """
        if section.code == 4:
            query_inject_quant += """
    AND loc.partner_id = %s
            """
        status_desc = {1: "Sold & NOT Paid", 2: "In Stock", 3: "Returned"}
        loc_usage = {1: "customer", 2: "internal", 3: "supplier", 4: "internal"}
        if section.code in [1, 3]:
            query_inject_quant_params = (
                self.id,
                section.id,
                self.env.uid,
                status_desc[section.code],
                loc_usage[section.code],
                "f",
                section.report_id.filter_partner_id.id,
                section.report_id.threshold_date,
            )
        elif section.code == 4:
            query_inject_quant_params = (
                self.id,
                section.id,
                self.env.uid,
                "",
                loc_usage[section.code],
                "t",
                section.report_id.filter_partner_id.id,
                section.report_id.filter_partner_id.id,
            )
        else:
            query_inject_quant_params = (
                self.id,
                section.id,
                self.env.uid,
                status_desc[section.code],
                loc_usage[section.code],
                "f",
                section.report_id.filter_partner_id.id,
            )
        self.env.cr.execute(query_inject_quant, query_inject_quant_params)

    def _update_invoice_info(self, section_id, code):
        query_update_quant = """
UPDATE
    stock_consignment_report_quant q1
SET
    currency = inv_info.curr,
    purchase_price = inv_info.price,
    remark = inv_info.supp_invoice
FROM (
    SELECT
        inv.currency AS curr,
        inv.price_unit AS price,
        inv.supp_invoice,
        q2.section_id,
        inv.lot_id
    FROM
        stock_consignment_report_quant q2
    INNER JOIN (
        SELECT DISTINCT ON (l.lot_id)
            c.name AS currency,
            l.price_unit,
            i.reference AS supp_invoice,
            l.lot_id
        FROM
            account_invoice_line l
        INNER JOIN
            account_invoice i ON l.invoice_id = i.id
        INNER JOIN
            res_currency c ON i.currency_id = c.id
        WHERE
            i.type = 'in_invoice'
            AND l.state in %s
        ORDER BY
            l.lot_id,
            i.date_invoice DESC,
            l.write_date DESC
    ) inv
        ON q2.lot_id = inv.lot_id
    WHERE
        q2.section_id = %s
) inv_info
WHERE
    q1.section_id = inv_info.section_id
    AND q1.lot_id = inv_info.lot_id
        """
        state_vals = {1: ("paid",), 2: ("draft", "open")}
        query_update_quant_params = (state_vals[code], section_id)
        self.env.cr.execute(query_update_quant, query_update_quant_params)

    def _update_age(self, model, section):
        quants = model.search([("section_id", "=", section.id)])
        for quant in quants:
            out_date = fields.Datetime.now()
            if section.code != 2:
                domain = [("active", "=", True)]
                if section.code == 1:
                    domain.append(("usage", "=", "customer"))
                elif section.code == 3:
                    domain.append(("usage", "=", "supplier"))
                elif section.code == 4:
                    domain.append(("return_location", "=", True))
                    domain.append(
                        ("partner_id", "=", section.report_id.filter_partner_id.id)
                    )
                locs = self.env["stock.location"].search(domain)
                move = self.env["stock.move.line"].search(
                    [
                        ("lot_id", "=", quant.lot_id.id),
                        ("code", "=", "outgoing"),
                        ("location_dest_id", "in", [loc.id for loc in locs]),
                        ("state", "=", "done"),
                    ],
                    order="date asc",
                    limit=1,
                )
                if move:
                    out_date = move.date
            quant.write({"outgoing_date": out_date})
            if out_date:
                stock_days = (
                    fields.Datetime.from_string(out_date)
                    - fields.Datetime.from_string(quant.incoming_date)
                ).days
                quant.write({"stock_days": stock_days})

    def _update_reservation(self, model, section_id):
        quants = model.search([("section_id", "=", section_id)])
        for quant in quants:
            if quant.reservation_id:
                quant.write({"remark": quant.reservation_id.sudo().name_get()[0][1]})
            elif quant.sale_id:
                remark = quant.sale_id.sudo().name
                if quant.sale_id.sudo().client_order_ref:
                    remark += " - " + quant.sale_id.sudo().client_order_ref
                quant.write({"remark": remark})

    def _delete_supplier_loc_quant(self, model, section_id):
        quants = model.search([("section_id", "=", section_id)])
        for quant in quants:
            find_duplicate = model.search(
                [
                    ("section_id", "in", [*range(section_id - 3, section_id)]),
                    ("lot_id", "=", quant.lot_id.id),
                ]
            )
            if find_duplicate:
                quant.unlink()

    def _update_remark(self, model, section_id, usage):
        quants = model.search([("section_id", "=", section_id)])
        move_obj = self.env["stock.move.line"]
        loc_ids = self.env["stock.location"].search([("usage", "=", usage)]).ids
        for quant in quants:
            move = move_obj.search(
                [
                    ("lot_id", "=", quant.lot_id.id),
                    ("location_dest_id", "in", loc_ids),
                    ("state", "=", "done"),
                ],
                order="date desc",
                limit=1,
            )
            if move and move.picking_id:
                quant.write({"remark": move.picking_id.note})


class PartnerXslx(models.AbstractModel):
    _name = "report.stock_consignment_report.stock_consignment_report"
    _inherit = "report.stock_abstract_report_xlsx"

    def __init__(self, pool, cr):
        super(PartnerXslx, self).__init__(pool, cr)

    def create(self, data):
        return super(PartnerXslx, self).create(data)

    def _get_report_name(self, report):
        report_name = _("Consignment Report")
        return self._get_report_complete_name(report, report_name)

    def _get_report_columns(self, report):
        return {
            0: {"header": _("Code"), "field": "product_code", "width": 10},
            1: {"header": _("Reference Name"), "field": "product_name", "width": 30},
            2: {"header": _("Case No."), "field": "lot", "width": 15},
            3: {"header": _("Purch Curr"), "field": "currency", "width": 8},
            4: {
                "header": _("Curr Price"),
                "field": "purchase_price",
                "type": "amount",
                "width": 15,
            },
            5: {"header": _("Status"), "field": "status", "width": 18},
            6: {"header": _("Remark"), "field": "remark", "width": 30},
            7: {"header": _("Incoming Date"), "field": "incoming_date", "width": 20},
            8: {
                "header": _("Age"),
                "field": "stock_days",
                "type": "number",
                "width": 8,
            },
            9: {"header": _("Outgoing Date"), "field": "outgoing_date", "width": 20},
        }

    def _get_report_filters(self, report):
        return [
            [_("Report Date"), report.current_date],
            [
                _("Partner"),
                _("[%s] %s")
                % (report.filter_partner_id.ref, report.filter_partner_id.name),
            ],
            [_("Threshold Date"), report.threshold_date],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _generate_report_content(self, workbook, report):
        title_vals = {
            1: "Part 1. Consignment Sold and Not Yet Paid",
            2: "Part 2. Consignment Available Stock",
            3: "Part 3. Consignment Back to Supplier",
            4: "Part 4. Repair Cases",
        }
        for section in report.section_ids:
            self.write_array_title(title_vals[section.code])

            if section.code in [1, 3, 4]:
                self.write_array_header()
            # adjust array header
            elif section.code == 2:
                self.columns[9] = {
                    "header": _("Current Date"),
                    "field": "outgoing_date",
                    "width": 20,
                }
                self.write_array_header()
                self.columns[9] = {
                    "header": _("Outgoing Date"),
                    "field": "outgoing_date",
                    "width": 20,
                }

            sorted_quants = sorted(
                section.quant_ids, key=lambda x: (x.product_name, x.lot)
            )
            for quant in sorted_quants:
                self.write_line(quant)

            # Line break
            self.row_pos += 2
