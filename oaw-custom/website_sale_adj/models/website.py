# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    about_us = fields.Text(string="About Us")
    contact_description = fields.Text(string="Contact Information")
    empty_page_message = fields.Text(string="Empty Shop Display Message")
    whatsapp_link = fields.Char(string="Whatsapp Link",)
    whatsapp_qr_image = fields.Binary(string="Whatsapp QR Code",)
    wechat_link = fields.Char(string="Wechat Link",)
    wechat_qr_image = fields.Binary(string="Wechat QR Code",)
