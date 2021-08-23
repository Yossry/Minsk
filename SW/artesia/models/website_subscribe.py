from odoo import fields, models


class WebsiteSubscribe(models.Model):
    _name = 'website.subscribe'

    name = fields.Char('Email')
