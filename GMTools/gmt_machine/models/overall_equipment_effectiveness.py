# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OverallEquipmentEffectiveness(models.Model):
    _name = 'overall.equipment.effectiveness'
    _description = 'Overall Equipment Effectiveness'
    _rec_name = 'machine_id'

    machine_id = fields.Many2one('product.template', 'Machine',
                                 ondelete='cascade',
                                 domain=[('type', '=', 'machine')])
    oee_run_time = fields.Float('Run Time')
    oee_idle_time = fields.Float('Idle Time')
    oee_down_time = fields.Float('Down Time')
    average_oee = fields.Integer('Average OEE')
