from odoo import fields, models


class ActivityArea(models.Model):
    _name = 'activity.area'
    _description = 'Area'

    name = fields.Char(string="Area name",
                       translate=True)
    full_name = fields.Char(string="Full name",
                            translate=True)
    country_id = fields.Many2one('res.country',
                                 string="Country")
