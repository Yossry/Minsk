# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # this field is added due to kanban view limitation
    # i.e. decimal place values cannot be eliminated by view adjustment
    list_price_integer = fields.Integer(
        string="Sale Price",
        compute="_get_list_price_integer",
        store=True,
        readonly=True,
    )
    net_price = fields.Float(
        string="Net Price", digits=dp.get_precision("Product Price")
    )
    sale_hkd_ab = fields.Integer(
        string="Stock Sale HKD AB", digits=dp.get_precision("Product Price"), store=True
    )
    sale_hkd_aa_so = fields.Integer(
        string="Stock Sale HKD AA Special Offer",
        digits=dp.get_precision("Product Price"),
        store=True,
    )
    sale_hkd_ac = fields.Integer(
        string="Stock Sale HKD AB", digits=dp.get_precision("Product Price"), store=True
    )
    sale_hkd_ac_so = fields.Integer(
        string="Stock Sale HKD AC Special Offer",
        digits=dp.get_precision("Product Price"),
        store=True,
    )
    net_price_integer = fields.Integer(  # for kanban presentation
        string="Net Price", compute="_get_net_price_integer", store=True, readonly=True
    )
    discount = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision("Discount"),
        compute="_get_discount",
        readonly=True,
    )
    discount_aa_so = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision("Discount"),
        compute="_get_discount_aa_so",
        readonly=True,
    )
    discount_ac = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision("Discount"),
        compute="_get_discount_ac",
        readonly=True,
    )
    discount_ac_so = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision("Discount"),
        compute="_get_discount_ac_so",
        readonly=True,
    )
    net_price_cny = fields.Float(
        string="Sale RMB",
        compute="_get_net_price_cny",
        digits=dp.get_precision("Product Price"),
    )
    sale_hkd_aa_so_cn = fields.Integer(
        string="Sale AB RMB",
        compute="_get_net_price_cny",
        digits=dp.get_precision("Product Price"),
    )
    sale_hkd_ac_cn = fields.Integer(
        string="Sale AC RMB",
        compute="_get_net_price_cny",
        digits=dp.get_precision("Product Price"),
    )
    sale_hkd_ac_so_cn = fields.Integer(
        string="Sale AB RMB",
        compute="_get_net_price_cny",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_usd = fields.Float(
        string="Sale USD",
        compute="_get_sale_price_currency",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_eur = fields.Float(
        string="Sale EUR",
        compute="_get_sale_price_currency",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_chf = fields.Float(
        string="Sale CHF",
        compute="_get_sale_price_currency",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_rmb = fields.Float(
        string="Sale RMB",
        compute="_get_sale_price_currency",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_usd_so = fields.Float(
        string="Sale USD",
        compute="_get_sale_price_currency_discounted",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_eur_so = fields.Float(
        string="Sale EUR",
        compute="_get_sale_price_currency_discounted",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_chf_so = fields.Float(
        string="Sale CHF",
        compute="_get_sale_price_currency_discounted",
        digits=dp.get_precision("Product Price"),
    )
    sale_in_rmb_so = fields.Float(
        string="Sale RMB",
        compute="_get_sale_price_currency_discounted",
        digits=dp.get_precision("Product Price"),
    )
    oversea_retail_price = fields.Float(
        string="Oversea Retail Price", compute="_get_oversea_retail"
    )
    oversea_retail_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Oversea Retail Currency",
        compute="_get_oversea_retail",
    )
    brand = fields.Char(related="categ_id.name", string="Brand")
    advertise = fields.Boolean(default=False)
    net_profit = fields.Float(
        string="Net Profit",
        digits=dp.get_precision("Product Price"),
        compute="_compute_net_profit",
        readonly=True,
        store=True,
    )
    net_profit_pct = fields.Float(
        string="Net Profit Percent",
        digits=dp.get_precision("Discount"),
        compute="_compute_net_profit",
        readonly=True,
    )
    stock_cost = fields.Float(
        string="Stock Cost",
        compute="_get_stock_cost",
        digits=dp.get_precision("Product Price"),
    )
    partner_stock_last_modified = fields.Datetime(
        string="Last Modified", readonly=True, store=True
    )

    @api.multi
    def _get_sale_price_currency(self):
        usd_rec = 0
        eur_rec = 0
        chf_rec = 0
        rmb_rec = 0
        if self.env["res.currency"].search([("name", "=", "USD")]):
            usd_rec = self.env["res.currency"].search([("name", "=", "USD")])
        if self.env["res.currency"].search([("name", "=", "EUR")]):
            eur_rec = self.env["res.currency"].search([("name", "=", "EUR")])
        if self.env["res.currency"].search([("name", "=", "CHF")]):
            chf_rec = self.env["res.currency"].search([("name", "=", "CHF")])
        if self.env["res.currency"].search([("name", "=", "CNY")]):
            rmb_rec = self.env["res.currency"].search([("name", "=", "CNY")])
        if usd_rec and eur_rec and chf_rec and rmb_rec:
            for pt in self:
                if usd_rec:
                    pt.sale_in_usd = pt.net_price * usd_rec.rate
                if eur_rec:
                    pt.sale_in_eur = pt.net_price * eur_rec.rate
                if chf_rec:
                    pt.sale_in_chf = pt.net_price * chf_rec.rate
                if rmb_rec:
                    pt.sale_in_rmb = pt.net_price * rmb_rec.rate

    @api.multi
    @api.depends("discount_aa_so")
    def _get_sale_price_currency_discounted(self):
        usd_rec = 0
        eur_rec = 0
        chf_rec = 0
        rmb_rec = 0
        if self.env["res.currency"].search([("name", "=", "USD")]):
            usd_rec = self.env["res.currency"].search([("name", "=", "USD")])
        if self.env["res.currency"].search([("name", "=", "USD")]):
            eur_rec = self.env["res.currency"].search([("name", "=", "EUR")])
        if self.env["res.currency"].search([("name", "=", "USD")]):
            chf_rec = self.env["res.currency"].search([("name", "=", "CHF")])
        if self.env["res.currency"].search([("name", "=", "USD")]):
            rmb_rec = self.env["res.currency"].search([("name", "=", "CNY")])
        for pt in self:
            if usd_rec:
                pt.sale_in_usd_so = pt.sale_hkd_aa_so * usd_rec.rate
            if eur_rec:
                pt.sale_in_eur_so = pt.sale_hkd_aa_so * eur_rec.rate
            if chf_rec:
                pt.sale_in_chf_so = pt.sale_hkd_aa_so * chf_rec.rate
            if rmb_rec:
                pt.sale_in_rmb_so = pt.sale_hkd_aa_so * rmb_rec.rate

    @api.multi
    def _get_net_price_cny(self):
        cny_rec = 0
        if self.env["res.currency"].search([("name", "=", "CNY")]):
            cny_rec = self.env["res.currency"].search([("name", "=", "CNY")])
        for pt in self:
            if cny_rec:
                pt.net_price_cny = pt.net_price * cny_rec.rate
                pt.sale_hkd_aa_so_cn = pt.sale_hkd_aa_so * cny_rec.rate
                pt.sale_hkd_ac_cn = pt.sale_hkd_ac * cny_rec.rate
                pt.sale_hkd_ac_so_cn = pt.sale_hkd_ac_so * cny_rec.rate

    @api.multi
    @api.depends("list_price", "net_price")
    def _get_discount(self):
        for pt in self:
            if not pt.list_price or not pt.net_price:
                pt.discount = 0.0
            else:
                pt.discount = (1 - pt.net_price / pt.list_price) * 100

    @api.multi
    @api.depends("list_price", "sale_hkd_aa_so")
    def _get_discount_aa_so(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_aa_so:
                pt.discount_aa_so = 0.0
            else:
                pt.discount_aa_so = (1 - pt.sale_hkd_aa_so / pt.list_price) * 100

    @api.multi
    @api.depends("list_price", "sale_hkd_ac")
    def _get_discount_ac(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_ac:
                pt.discount_ac = 0.0
            else:
                pt.discount_ac = (1 - pt.sale_hkd_ac / pt.list_price) * 100

    @api.multi
    @api.depends("list_price", "sale_hkd_ac_so")
    def _get_discount_ac_so(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_ac_so:
                pt.discount_ac_so = 0.0
            else:
                pt.discount_ac_so = (1 - pt.sale_hkd_ac_so / pt.list_price) * 100

    @api.multi
    @api.depends("list_price")
    def _get_list_price_integer(self):
        for pt in self:
            pt.list_price_integer = int(pt.list_price)

    @api.multi
    @api.depends("net_price")
    def _get_net_price_integer(self):
        for pt in self:
            pt.net_price_integer = int(pt.net_price)

    @api.multi
    def _get_oversea_retail(self):
        for pt in self:
            if pt.product_variant_ids:
                supplier_stock = (
                    self.env["supplier.stock"]
                    .sudo()
                    .search(
                        [
                            ("product_id", "=", pt.product_variant_ids[0].id),
                            ("quantity", "!=", 0),
                        ],
                        order="retail_unit_base",
                        limit=1,
                    )
                )
                pt.oversea_retail_price = supplier_stock.retail_in_currency
                pt.oversea_retail_currency_id = supplier_stock.currency_id

    @api.multi
    @api.depends("net_price", "stock_cost")
    def _compute_net_profit(self):
        for pt in self:
            if pt.net_price == 0.0 or pt.stock_cost == 0.0:
                pt.net_profit = 0.00
                pt.net_profit_pct = 0.00
            else:
                pt.net_profit = pt.net_price - pt.stock_cost
                pt.net_profit_pct = (pt.net_price / pt.stock_cost) * 100 - 100
        return

    def _get_quant_cost(self, prod_ids):
        quant = self.env["stock.quant"].search(
            [("product_id", "in", prod_ids), ("usage", "=", "internal")],
            order="cost",
            limit=1,
        )
        if quant:
            return quant.cost
        return False

    def _get_supp_stock_cost(self, prod_ids):
        records = self.env["supplier.stock"].search(
            [("product_id", "in", prod_ids), ("quantity", ">", 0)]
        )
        if records:
            return min(r.price_unit_base for r in records)
        return False

    @api.multi
    def _get_stock_cost(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            supp_stock_cost = self._get_supp_stock_cost(prod_ids)
            if supp_stock_cost:
                pt.stock_cost = supp_stock_cost
                continue
            quant_cost = self._get_quant_cost(prod_ids)
            if quant_cost:
                pt.stock_cost = quant_cost
                continue
            pt.stock_cost = pt.standard_price
