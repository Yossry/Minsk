from odoo import api, fields, models
from odoo.exceptions import AccessDenied


class Endpoint(models.Model):
    _name = 'shipbox.endpoint'

    name = fields.Char('Name')
    url = fields.Char('URL')

    @api.model
    def get_endpoint(self):
        if not self.env.user.has_group('base.group_user'):
            raise AccessDenied()
        user = self.env.user[0]
        return {'name': user.shipbox_id.name if user.shipbox_id else False,
                'url': user.shipbox_id.url if user.shipbox_id else False,
                }
