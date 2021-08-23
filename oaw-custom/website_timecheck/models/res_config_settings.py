# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    homepage_url = fields.Char(
        string="Homepage",
        related="website_id.homepage_url",
        readonly=False,
        help="Defines the homepage for the website, leave it empty to be set "
        "as default ('/')",
    )
