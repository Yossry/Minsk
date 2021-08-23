# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# Inspiration from OCA/project/project_task_code
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import logging


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char(required=True, default="/", readonly=False)

    # _sql_constraints = [
    #     (
    #         'res_partner_unique_ref',
    #         'UNIQUE (ref)',
    #         _('The ref must be unique!')
    #     ),
    # ]

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Changing ref of %s", self)
        for vals in vals_list:
            if vals.get("ref", "/") == "/":
                vals["ref"] = self.env["ir.sequence"].next_by_code(
                    "partner.reference"
                )
        return super().create(vals_list)

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default["ref"] = self.env["ir.sequence"].next_by_code(
            "partner.reference"
        )
        return super().copy(default)
