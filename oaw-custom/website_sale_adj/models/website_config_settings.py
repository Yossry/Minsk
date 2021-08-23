# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    about_us = fields.Text(
        string="About Us", related="website_id.about_us", readonly=False
    )
    contact_description = fields.Text(
        string="Contact Information",
        related="website_id.contact_description",
        readonly=False,
    )
    empty_page_message = fields.Text(
        string="Empty Shop Display Message",
        related="website_id.empty_page_message",
        readonly=False,
    )
    whatsapp_link = fields.Char(
        string="Whatsapp Link", related="website_id.whatsapp_link", readonly=False,
    )
    whatsapp_qr_image = fields.Binary(
        string="Whatsapp QR Code",
        related="website_id.whatsapp_qr_image",
        readonly=False,
    )
    wechat_link = fields.Char(
        string="Wechat Link", related="website_id.wechat_link", readonly=False,
    )
    wechat_qr_image = fields.Binary(
        string="Wechat QR Code", related="website_id.wechat_qr_image", readonly=False,
    )
