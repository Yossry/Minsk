# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    website_published = fields.Boolean("Visible in Portal / Website", copy=False,)
    readonly_record = fields.Boolean("Readonly Record", copy=False, default=False,)
    website_quantity = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", ">=3")],
        string="Webiste Quantity",
        readonly=True,
    )
    retail_chf = fields.Float(
        related="product_id.product_tmpl_id.retail_chf",
        string="Retail CHF",
        digits=dp.get_precision("Product Price"),
    )
    retail_eur = fields.Float(
        related="product_id.product_tmpl_id.retail_eur",
        string="Retail EUR",
        digits=dp.get_precision("Product Price"),
    )
    retail_usd = fields.Float(
        related="product_id.product_tmpl_id.retail_usd",
        string="Retail USD",
        digits=dp.get_precision("Product Price"),
    )
    retail_rmb = fields.Float(
        related="product_id.product_tmpl_id.retail_rmb",
        string="Retail RMB",
        digits=dp.get_precision("Product Price"),
    )

    cost_hkd = fields.Float(
        related="product_id.product_tmpl_id.net_price",
        string="My Cost in HKD",
        digits=dp.get_precision("Product Price"),
        store=True,
    )
    cost_chf = fields.Float(
        string="My Cost in CHF",
        digits=dp.get_precision("Product Price"),
        compute="_compute_cost_price",
        store=True,
    )
    cost_eur = fields.Float(
        string="My Cost in EUR",
        digits=dp.get_precision("Product Price"),
        compute="_compute_cost_price",
        store=True,
    )
    cost_usd = fields.Float(
        string="My Cost in USD",
        digits=dp.get_precision("Product Price"),
        compute="_compute_cost_price",
        store=True,
    )
    special_offer_currency_id = fields.Many2one("res.currency")

    @api.multi
    @api.depends("cost_hkd")
    def _compute_cost_price(self):
        currency = self.env.user.company_id.currency_id
        for supplier_stock in self:
            supplier_stock.cost_chf = currency._convert(
                supplier_stock.cost_hkd,
                self.env.ref("base.USD"),
                self.env.user.company_id,
                fields.Date.today(),
            )
            supplier_stock.cost_eur = currency._convert(
                supplier_stock.cost_hkd,
                self.env.ref("base.EUR"),
                self.env.user.company_id,
                fields.Date.today(),
            )
            supplier_stock.cost_usd = currency._convert(
                supplier_stock.cost_hkd,
                self.env.ref("base.USD"),
                self.env.user.company_id,
                fields.Date.today(),
            )
