# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ActivityLog(models.Model):
    _name = 'activity.log'
    _description = 'Activity Logs'
    _rec_name = 'machine_id'

    machine_id = fields.Many2one('product.template', 'Machine',
                                 ondelete='cascade',
                                 domain=[('type', '=', 'machine')])
    activity_type = fields.Selection([('edit', 'Edit'),
                                      ('auto', 'Auto'),
                                      ('manual', 'Manual')], 'Activity Type')
    time = fields.Float("Time")
    duration = fields.Float("Duration")
    activitylog_count = fields.Integer('Activity Log')
