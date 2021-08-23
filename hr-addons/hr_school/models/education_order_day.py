# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class EducationOrderDay(models.Model):
    _name = 'education.order.day'
    _description = 'Order of the day'

    school_id = fields.Many2one(
        comodel_name='res.partner', string='School',
        domain=[('educational_category', '=', 'school')], required=True)
    month_id = fields.Many2one(
        comodel_name='base.month', string='Month', required=True)
    meeting_day = fields.Selection(
        string='Meeting day',
        selection=[('1', '1'),
                   ('15', '15')], default='1', required=True)
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course', required=True)
    type = fields.Selection(
        string='Type',
        selection=[('family', 'Family'),
                   ('student', 'Student')], required=True)
    order_day = fields.Text(
        string='Order of the day', required=True)
