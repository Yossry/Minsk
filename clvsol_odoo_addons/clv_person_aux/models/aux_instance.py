# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    aux_instance_id = fields.Many2one(
        comodel_name='clv.aux.instance',
        string='Aux Instance',
        required=False,
    )
