# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64

from odoo import _, api, fields, models
from odoo import tools


class ResCompany(models.Model):
    _inherit = "res.company"

    logo_web = fields.Binary(compute='_compute_logo_web', store=True)
    theme_logo = fields.Binary(string='Theme Logo')
    theme_icon = fields.Binary(string='Theme Icon')

    @api.depends('theme_logo', 'partner_id', 'partner_id.image')
    def _compute_logo_web(self):
        for company in self:
            if company.theme_logo:
                image = base64.b64decode(company.theme_logo) or None
                company.logo_web = tools.image_resize_image(base64.b64encode(image), (180, None))
            else:
                company.logo_web = tools.image_resize_image(company.partner_id.image, (180, None))
