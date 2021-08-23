# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class QualityControl(models.Model):
    _name = 'quality.control'
    _description = 'Quality Control'
    _rec_name = 'machine_id'

    machine_id = fields.Many2one('product.template', 'Machine',
                                 ondelete='cascade',
                                 domain=[('type', '=', 'machine')])
    error_number = fields.Integer('Error Number')
    error_time = fields.Float("Time")
    error_date = fields.Date("Date")
    qc_count = fields.Integer("QC Count")
