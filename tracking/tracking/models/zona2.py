## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
_logger = logging.getLogger(__name__)
class ResZona2(models.Model):
    _name = "res.zona2"
    name= fields.Char(string="Nombre")
    user_id =fields.Many2one('hr.employee', string="Usuario",domain=[('department_id', '=',3)])
    pos_id = fields.Many2one('pos.config', string="Punto de Venta" )