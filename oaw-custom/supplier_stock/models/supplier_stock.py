# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SupplierStock(models.Model):
    _name = "supplier.stock"
    _inherit = "mail.thread"
    _description = "Partner Stock"
    _order = "id desc"

    currency_name = fields.Char(related="currency_id.name")
    last_update_date = fields.Datetime(readonly=True, string="Last Update Date")
    last_update_user_id = fields.Many2one(
        "res.users", readonly=True, string="Last Update User"
    )
    prod_cat_selection = fields.Many2one(
        comodel_name="product.category", string="Category ID", required=True
    )
    brand = fields.Char(related="prod_cat_selection.name", string="Brand")
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True
    )
    partner_loc_id = fields.Many2one(
        comodel_name="supplier.location",
        default=lambda self: self._get_loc_id(),
        string="Partner Location",
        required=True,
    )
    short_loc_name = fields.Char("Location", related="partner_loc_id.short_loc")
    # For Partner Stock filter
    qty_up_date = fields.Datetime(string="Quantity increased", store=True)
    qty_down_date = fields.Datetime(string="Quantity decreased")
    costprice_up_date = fields.Datetime(string="Costprice increased", readonly=True)
    costprice_down_date = fields.Datetime(string="Costprice decreased", readonly=True)
    note_updated_date = fields.Datetime(string="Partner Note updated")
    partner_qty = fields.Char(string="Evaluated Quantity", store=True)
    lowest_cost = fields.Boolean(string="Cheapest entry", store=True)
    # Flags those ps that have multiple entries with same product_id
    has_duplicates = fields.Boolean(string="Has Duplicates", store=True)
    supplier_lead_time = fields.Integer(
        string="Lead Time", related="partner_loc_id.supplier_lead_time", readonly=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Code", required=True
    )
    product_name = fields.Char(
        string="Product Name", related="product_id.product_tmpl_id.name", store=True
    )
    product_list_price = fields.Float(
        string="Retail in HKD",
        related="product_id.list_price",
        readonly=True,
        store=True,
    )
    product_list_price_discount = fields.Float(
        string="Discount in HKD (%)",
        digits=dp.get_precision("Discount"),
        compute="_compute_discount",
        readonly=True,
        store=True,
    )
    quantity = fields.Float(
        string="Quantity", digits=dp.get_precision("Product Price"), required=True
    )
    price_unit = fields.Float(
        string="Sales Price in currency",
        required=True,
        digits=dp.get_precision("Product Price"),
        store=True,
    )
    price_subtotal = fields.Float(
        string="Amount",
        digits=dp.get_precision("Product Price"),
        store=True,
        readonly=True,
        compute="_compute_price",
    )
    price_unit_base = fields.Float(
        string="Sales Price in HKD",
        digits=dp.get_precision("Product Price"),
        compute="_compute_price_base",
        store=True,
    )
    retail_unit_base = fields.Float(
        string="Retail Price (Base)",
        digits=dp.get_precision("Product Price"),
        compute="_compute_retail_base",
        store=True,
    )
    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )
    partner_note = fields.Text(string="Partner Note")
    retail_in_currency = fields.Float(
        string="Retail in Currency",
        required=True,
        digits=dp.get_precision("Product Price"),
        store=True,
    )
    discount_in_curr = fields.Float(
        string="Discount in currency (%)",
        digits=dp.get_precision("Discount"),
        compute="_discount_in_curr",
        store=True,
        readonly=True,
    )
    new_description = fields.Char(
        string="Reference",
        related="product_id.product_tmpl_id.name",
        readonly=True,
        store=True,
    )
    hk_location = fields.Boolean(related="partner_loc_id.hk_location")

    @api.onchange("prod_cat_selection")
    def on_change_category(self):
        ids = []
        if self.product_id.categ_id != self.prod_cat_selection:
            if self.prod_cat_selection and not self.product_id:
                products = self.env["product.product"].search(
                    [("categ_id", "=", self.prod_cat_selection.id)]
                )
                ids.append(("id", "in", products.ids))
                return {"domain": {"product_id": ids}}
            if self.prod_cat_selection and self.product_id:
                self.product_id = False
                products = self.env["product.product"].search(
                    [("categ_id", "=", self.prod_cat_selection.id)]
                )
                ids.append(("id", "in", products.ids))
                return {"domain": {"product_id": ids}}
        if not self.prod_cat_selection:
            self.product_id = False

    @api.depends("price_unit", "quantity", "currency_id")
    def _compute_price(self):
        self.price_subtotal = self.price_unit * self.quantity
        if self.currency_id:
            self.price_subtotal = self.currency_id.round(self.price_subtotal)

    @api.onchange("partner_loc_id")
    def _onchange_partner_loc_id(self):
        if not self.partner_loc_id:
            self.currency_id = False
        else:
            self.currency_id = self.partner_loc_id.currency_id

    @api.model
    def _get_loc_id(self):
        locs = self.env["supplier.location"].search(
            [("owner_id", "=", self.env.user.partner_id.id)]
        )
        if locs:
            return locs[0]
        else:
            return False

    @api.multi
    @api.depends("price_unit", "currency_id")
    def _compute_price_base(self):
        curr_obj = self.env["res.currency"]
        company_curr = self.env.user.company_id.currency_id
        for rec in self:
            if rec.currency_id and rec.price_unit:
                rec.price_unit_base = curr_obj.browse(rec.currency_id.id).compute(
                    rec.price_unit, company_curr
                )
        return

    @api.multi
    @api.depends("product_list_price", "price_unit_base")
    def _compute_discount(self):
        for ss in self:
            if ss.product_list_price == 0.0 or ss.price_unit_base == 0.0:
                ss.product_list_price_discount = 0.0
            else:
                ss.product_list_price_discount = (
                    1 - (ss.price_unit_base / ss.product_list_price)
                ) * 100
        return

    @api.multi
    @api.depends("retail_in_currency", "price_unit")
    def _discount_in_curr(self):
        for rec in self:
            if rec.retail_in_currency == 0.0 or rec.price_unit == 0.0:
                rec.discount_in_curr = 0.0
            else:
                rec.discount_in_curr = (
                    1 - (rec.price_unit / rec.retail_in_currency)
                ) * 100
        return

    @api.model
    def update_price_unit_base(self):
        supplier_stock = self.search([])
        supplier_stock._compute_price_base()
        return True

    @api.multi
    @api.depends("retail_in_currency", "currency_id")
    def _compute_retail_base(self):
        curr_obj = self.env["res.currency"]
        company_curr = self.env.user.company_id.currency_id
        for rec in self:
            if rec.currency_id and rec.retail_in_currency:
                rec.retail_unit_base = curr_obj.browse(rec.currency_id.id).compute(
                    rec.retail_in_currency, company_curr
                )
        return

    @api.multi
    def _get_quantity(self):
        for ps in self:
            if ps.quantity == 0.0:
                ps.partner_qty = "0"
            elif ps.quantity == 1.0:
                ps.partner_qty = "1"
            elif ps.quantity == 2.0:
                ps.partner_qty = "2"
            elif ps.quantity >= 3.0:
                ps.partner_qty = ">=3"
            ps_products = self.sudo().search(
                [("product_id", "=", ps.product_id.id)], order="price_unit_base ASC"
            )
            if ps_products:
                for psc in ps_products:
                    if len(ps_products) >= 2:
                        psc.sudo().write({"lowest_cost": False, "has_duplicates": True})
                    else:
                        psc.sudo().write(
                            {"lowest_cost": False, "has_duplicates": False}
                        )
                ps_products[0].sudo().write({"lowest_cost": True})

    @api.model
    def create(self, vals):
        vals.update(
            {
                "last_update_date": fields.Datetime.now(),
                "last_update_user_id": self.env.user.id,
            }
        )
        res = super(SupplierStock, self).create(vals)
        # res._get_quantity()
        return res

    @api.multi
    def write(self, vals):
        if (
            "quantity" in vals
            or "price_unit" in vals
            or "partner_loc_id" in vals
            or "prod_cat_selection" in vals
            or "product_id" in vals
            or "currency_id" in vals
            or "retail_in_currency" in vals
            or "partner_note" in vals
        ):
            vals.update(
                {
                    "last_update_date": fields.Datetime.now(),
                    "last_update_user_id": self.env.user.id,
                }
            )
            for ps in self:
                ps.product_id.product_tmpl_id.sudo().write(
                    {"partner_stock_last_modified": fields.Datetime.now()}
                )
                if "quantity" in vals:
                    if ps.quantity < vals["quantity"]:
                        ps.qty_up_date = fields.Datetime.now()
                    if ps.quantity > vals["quantity"]:
                        ps.qty_down_date = fields.Datetime.now()
                if "price_unit" in vals:
                    if ps.price_unit < vals["price_unit"]:
                        ps.costprice_up_date = fields.Datetime.now()
                    if ps.price_unit > vals["price_unit"]:
                        ps.costprice_down_date = fields.Datetime.now()
                if "partner_note" in vals:
                    ps.note_updated_date = fields.Datetime.now()
        res = super(SupplierStock, self).write(vals)
        for ps in self:
            if "quantity" in vals:
                ps._get_quantity()
        return res

    @api.multi
    def unlink(self):
        product_ids = []
        for ps in self:
            product_ids.append(ps.product_id.id)
        res = super(SupplierStock, self).unlink()
        related_ps = self.search([("product_id", "in", product_ids)])
        if related_ps:
            related_ps._get_quantity()
        return res
