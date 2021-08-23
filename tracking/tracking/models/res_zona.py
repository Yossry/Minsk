## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
_logger = logging.getLogger(__name__)
class ResZona(models.Model):
    _name = "res.zona"
    codigo = fields.Integer(
        string='Código',
    )
    name = fields.Char(string="Nombre")
    user_id = fields.Many2one('hr.employee', string="Usuario", domain=[('department_id', '=',2)])
    pos_id = fields.Many2one('pos.config', string="Punto de Venta"  )
    type = fields.Selection([
        ('VERE', 'Vendedor'),
        ('VE', 'Preventa'),
        ('RE', 'Reparto')
    ], string='Type', copy=False, default='VERE')

