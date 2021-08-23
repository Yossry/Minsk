## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
import logging
_logger = logging.getLogger(__name__)
class PosSession(models.Model):
	_inherit = 'pos.session'
	sync = fields.Boolean(string="Sync Warehouse", default=False)
	last_sysc = fields.Date(string="Last Sync")


	@api.constrains('user_id', 'state')
	def _check_unicity(self):
		# open if there is no session in 'opening_control', 'opened', 'closing_control' for one user
		if self.search_count([
				('state', 'not in', ('closed', 'closing_control')),
				('user_id', '=', self.user_id.id),
				('rescue', '=', False)
			]) > 50:
			raise ValidationError(_("You cannot create two active sessions with the same responsible."))

	@api.multi
	def login(self):
		for rec in self:
			rec.ensure_one()
			rec.write({
				'login_number': rec.login_number + 1,
			})