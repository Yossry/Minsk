# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AnalyticPlanMassCreateTemplate(models.Model):
    _name = "analytic.plan.mass.create.template"
    _description = "Template to create multiple analytic plan lines"

    name = fields.Char(
        'Name',
        required=True
    )
    labor_cost_product_id = fields.Many2one(
        'product.product',
        'Default Labor Cost Product',
        required=True
    )
    material_cost_product_id = fields.Many2one(
        'product.product',
        'Default Material Cost Product',
        required=True
    )
    revenue_product_id = fields.Many2one(
        'product.product',
        'Default Material Revenue Product',
        required=True
    )
    version_id = fields.Many2one(
        'account.analytic.plan.version',
        'Default Planning Version',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True
    )
