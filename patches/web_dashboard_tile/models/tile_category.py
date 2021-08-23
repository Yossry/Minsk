##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class TileCategory(models.Model):

    _name = 'tile.category'
    _description = 'Dashboard Tile Category'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer(
        help="Used to order the tile categories",
        default=0)
    fold = fields.Boolean('Folded by default')
