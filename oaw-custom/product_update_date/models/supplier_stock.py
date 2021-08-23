# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    updated_date = fields.Datetime(
        default=fields.Datetime.now(),
        compute="update_updated_date",
        store=True,
        string="Updated Date",
    )

    @api.multi
    @api.depends("product_id.product_tmpl_id.updated_date")
    def update_updated_date(self):
        for rec in self:
            rec.updated_date = fields.Datetime.now()

    @api.multi
    def write(self, vals):
        if not vals.get("updated_date"):
            vals["updated_date"] = fields.Datetime.now()
        return super(SupplierStock, self).write(vals)
