###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class PartnerWebDomain(models.Model):
    _name = "partner.web.domain"
    _description = "Web domain line"

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
