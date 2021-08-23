# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import api, fields, models
from odoo import tools
from odoo.modules.module import get_module_resource


class MediaFile(models.Model):
    _inherit = 'clv.mfile'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('clv_mfile', 'static/img', 'mfile_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        string='Photo',
        default=_default_image,
        attachment=True,
        help='This field holds the image used as avatar for this media file, limited to 1024x1024px.'
    )
    image_medium = fields.Binary(
        string='Medium-sized photo',
        attachment=True,
        help='Medium-sized photo of the media file. It is automatically '
             'resized as a 128x128px image, with aspect ratio preserved. '
             'Use this field in form views or some kanban views.'
    )
    image_small = fields.Binary(
        string='Small-sized photo',
        attachment=True,
        help='Small-sized photo of the media file. It is automatically '
             'resized as a 64x64px image, with aspect ratio preserved. '
             'Use this field anywhere a small image is required.')

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super().write(vals)
