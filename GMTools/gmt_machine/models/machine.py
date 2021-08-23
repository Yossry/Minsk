# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('machine', 'Machine')])
    machine_supervisor_id = fields.Many2one('res.users', 'Machine Supervisor')
    machine_users_ids = fields.Many2many('res.users', 'machine_users_rel',
                                         'machine_id', 'user_id',
                                         string='Machine Users')
    program_name = fields.Char('Program name')
    mode = fields.Char("Mode")
    draft_number = fields.Char("Dra. Number")
    part_counter = fields.Char("Part Counter")
    cycle_time = fields.Float("Cycle Time")
    feed_override = fields.Char("Feed Override")
    rpm_override = fields.Char("RPM Override")
    machine_image_ids = fields.One2many('machine.image', 'machine_id',
                                        'Machines')
