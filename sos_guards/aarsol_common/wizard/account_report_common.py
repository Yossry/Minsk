# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountCommonReport(models.TransientModel):
	_inherit = "account.common.report"

	date_from = fields.Date(string='Start Date',required=True)
	date_to = fields.Date(string='End Date',required=True)
	target_move = fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries'),], string='Target Moves', required=True, default='all')