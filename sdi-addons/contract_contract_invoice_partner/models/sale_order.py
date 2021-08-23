###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_contract_value(self, contract_template):
        self.ensure_one()
        data = super()._prepare_contract_value(contract_template)
        data['partner_id'] = self.partner_invoice_id.id
        return data
