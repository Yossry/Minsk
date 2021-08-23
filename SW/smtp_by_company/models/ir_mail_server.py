# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

from odoo import fields, models

class ir_mail_server(models.Model):

    _inherit = "ir.mail_server"

    company_id = fields.Many2one('res.company', string="Company")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: