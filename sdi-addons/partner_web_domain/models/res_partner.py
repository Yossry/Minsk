###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_web_domain_ids = fields.One2many(
        comodel_name='partner.web.domain',
        inverse_name='partner_id',
        string='Web domain lines',
    )
