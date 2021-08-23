# -*- coding: utf-8 -*-
# Copyright 2019 UNIBRAVO

from odoo import models, fields

class ResUsers(models.Model):

    _inherit = 'res.users'
    sidebar_visible = fields.Boolean("Show Sidebar Menu", default=False)
    chatter_position = fields.Selection([
        ('normal', 'Normal'),
        ('sided', 'Sided'),
    ], string="Chatter Position", default='normal')

    def __init__(self, pool, cr):

        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['chatter_position'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['chatter_position'])

        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sidebar_visible'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sidebar_visible'])
        return init_res