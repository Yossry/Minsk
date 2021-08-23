# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MachineImage(models.Model):
    _name = 'machine.image'
    _description = 'Machine Image'
    _rec_name = 'machine_id'

    machine_id = fields.Many2one('product.template', 'Machine',
                                 ondelete='cascade',
                                 domain=[('type', '=', 'machine')])
    image_medium = fields.Binary('Machine')
    description = fields.Text('Description')
