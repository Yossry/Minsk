# Copyright 2019-2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    product_category_ids = fields.Many2many(
        "product.category", string="Accessible Product Category"
    )
    related_partner = fields.Many2one("res.partner", string="Related Partner")
    product_all_category_ids = fields.Many2many(
        "product.category",
        compute="_compute_product_all_category_ids",
        readonly=True,
        store=True,
    )

    @api.multi
    def write(self, vals):
        if "product_category_ids" in vals:
            ir_rule = self.env.ref(
                "supplier_user_access.res_partner_supplier_fm_product_rule"
            )
            ir_rule.clear_caches()
        return super(ResPartner, self).write(vals)

    @api.multi
    @api.depends("product_category_ids")
    def _compute_product_all_category_ids(self):
        for partner in self:
            category_list = []
            for product_category_id in partner.product_category_ids:
                category_list += self._get_child_category(product_category_id.id)
            category_ids = self.env["product.category"].browse(category_list)
            partner.product_all_category_ids = category_ids

    @api.model
    def _get_child_category(self, product_category_id):
        query = """
            WITH RECURSIVE children AS (
                SELECT
                    id,
                    1 AS depth
                FROM
                    product_category
                WHERE
                    parent_id=%s
                UNION ALL
                    SELECT
                        a.id,
                        depth+1
                    FROM
                        product_category a
                JOIN
                    children b ON(a.parent_id = b.id)
            )
            SELECT * FROM children
        """
        self._cr.execute(query % product_category_id)
        result = self._cr.dictfetchall()
        category_ids = [i["id"] for i in result]
        category_ids.append(product_category_id)
        return category_ids
