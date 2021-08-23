
from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit='sale.order'
    @api.multi
    def open_uxltra(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url':   '/track',
        }
#if __name__ == "__main__":
#    track()