## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = "stock.picking"
    deliveryman_id = fields.Many2one('res.users', string="Repartidor")
    zona = fields.Char(string="Zona")
    lxtrackprocess = fields.Boolean(string="LXtrac process")
    amount = fields.Float(string="Monto")

    @api.model
    def create(self, vals):
        if vals['partner_id']:
            partner2 =vals['partner_id']
            partner= self.env['res.partner'].search([('id','=',partner2)])
            vals['zona'] = partner.zona
        return super(StockPicking, self).create(vals)

