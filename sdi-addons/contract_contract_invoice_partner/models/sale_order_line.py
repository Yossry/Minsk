###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('contract_id')
    def _check_contract_sale_partner(self):
        for rec in self:
            if rec.contract_id:
                partner = rec.contract_id.partner_id
                if rec.order_id.partner_id != partner and \
                   rec.order_id.partner_invoice_id != partner:
                    raise ValidationError(
                        _(
                            'Sale Order and contract should be '
                            'linked to the same partner or invoice partner.'
                        )
                    )
