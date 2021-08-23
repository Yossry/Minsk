# -*- coding: utf-8 -*-

from odoo import models, fields, api


class sms_setings(models.Model):
    _inherit = 'res.company'

    account_sid = fields.Char(string='Account Sid',
                                               default=lambda self: self.env['res.config.settings'].browse(
                                                   self.env['res.config.settings'].search([])[
                                                       -1].id).account_sid if self.env[
                                                   'res.config.settings'].search([]) else "")

    auth_token = fields.Char(string='Auth Token',
                              default=lambda self: self.env['res.config.settings'].browse(
                                  self.env['res.config.settings'].search([])[
                                      -1].id).auth_token if self.env[
                                  'res.config.settings'].search([]) else "")

    from_ = fields.Char(string='From',
                              default=lambda self: self.env['res.config.settings'].browse(
                                  self.env['res.config.settings'].search([])[
                                      -1].id).from_ if self.env[
                                  'res.config.settings'].search([]) else "")



