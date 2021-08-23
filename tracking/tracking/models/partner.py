## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
_logger = logging.getLogger(__name__)
class ResPartner(models.Model):
    _inherit="res.partner"
    partner_type_lx = fields.Selection([('rutas','Ruta'),('maquila','Maquila'),('autoservicios','Autoservicios'),('mayorista','Mayorista'),('noident','No Identificado')], string="Tipo Cliente", default='rutas')
    phone = fields.Char(string="Telefono")
    name_commercial = fields.Char(string="Nombre Comercial")
    sector_id = fields.Many2one('partner.sector', string="Sector")
    categorysector_id = fields.Many2one('category.sector', string="Categoria del Sector")
    zona = fields.Many2one('res.zona', string="Zona Preventa/Venta")
    zonalac = fields.Many2one('res.zona', string="Zona Preventa/Venta Lacteos")
    zona2 = fields.Many2one('res.zona', string="Zona Reparto")
    day1 = fields.Selection(string="Día de Entrega 1 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day2 = fields.Selection(string="Día de Entrega 2 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day3 = fields.Selection(string="Día de Entrega 3 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day4 = fields.Selection(string="Día de Entrega 4 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day5 = fields.Selection(string="Día de Entrega 5 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day6 = fields.Selection(string="Día de Entrega 6 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    day7 = fields.Selection(string="Día de Entrega 7 ",
                            selection=[('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'),
                                       ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'),
                                       ('sunday', 'Domingo')])
    dia_lunes = fields.Boolean(string="Día de Entrega 1", default=False)
    dia_martes = fields.Boolean(string="Día de Entrega 2", default=False)
    dia_miercoles = fields.Boolean(string="Día de Entrega 3", default=False)
    dia_jueves = fields.Boolean(string="Día de Entrega 4", default=False)
    dia_viernes = fields.Boolean(string="Día de Entrega 5", default=False)
    dia_sabado = fields.Boolean(string="Día de Entrega 6", default=False)
    dia_domingo = fields.Boolean(string="Día de Entrega 7", default=False)

    dia_ruta2_lunes = fields.Boolean(string="Día Entrega Lacteos 1", default=False)
    dia_ruta2_martes = fields.Boolean(string="Día Entrega Lacteos 2", default=False)
    dia_ruta2_miercoles = fields.Boolean(string="Dde Entrega Lacteos 3", default=False)
    dia_ruta2_jueves = fields.Boolean(string="Día Entrega Lacteos 4", default=False)
    dia_ruta2_viernes = fields.Boolean(string="Día Entrega Lacteos 5", default=False)
    dia_ruta2_sabado = fields.Boolean(string="Día Entrega Lacteos 6", default=False)
    dia_ruta2_domingo = fields.Boolean(string="Día Entrega Lacteos 7", default=False)

    sellersecundary_id = fields.Many2one('res.users', string="Vendedor Secundario")
    process = fields.Boolean(string="A procesar", default=False)
    date = fields.Date(string="Fecha")
    channelsales_id = fields.Selection(string="Canal de Ventas",
                                       selection=[('local', 'Locales'), ('autoservice', 'Autoservicio'), ('distribuitor', 'Distribuidores'),
                                       ('export', 'Exportaciones'), ('special', 'Especiales')])
    whithout_invoice = fields.Boolean(string="Sin Factura", default=False)

    usa_folio = fields.Boolean(string="Usa Folio ?", default=False, help="Se marca cuando el cliente usa un folio para registrar su venta, por ejemplo OXXO.")

    codigo_comprador = fields.Many2one('codigo.comprador',string="Codigo Comprador")
    plaza = fields.Char(string="Plaza")

    @api.model
    def create(self, vals):
        child_id = []
        if 'child_ids' in vals:
            vals['type'] = 'contact';
            print(vals)
            child_id.append(vals['child_ids'])
            if len(child_id[0]) == 0:
                raise UserError('Es necesario dar de alta una  Dirección de Entrega')
        return super(ResPartner, self).create(vals)

class CodigoComprador(models.Model):
  """Modelo para codigo de comprador"""
  _name = 'codigo.comprador'

  name = fields.Char(
      string='Codigo',
  )
    