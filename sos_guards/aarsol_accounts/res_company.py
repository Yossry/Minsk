
from odoo import models, fields, api

class default_report_sett(models.Model):
	_inherit= 'res.company'

	@api.model
	def _default_journal_template(self):
		def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'aarsol_accounts.JOURNAL\_%\_document' ), ('type', '=', 'qweb')], order='id asc', limit=1)
		return def_tpl

	@api.model
	def _default_payment_template(self):
		def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.PAYMENT\_%\_document' ), ('type', '=', 'qweb')], order='id asc', limit=1)
		return def_tpl

	template_journal = fields.Many2one('ir.ui.view', 'Journal Template', default=_default_journal_template,
		domain="[('type', '=', 'qweb'), ('key', 'like', 'aarsol_accounts.JOURNAL\_%\_document' )]")

	template_payment = fields.Many2one('ir.ui.view', 'Payment Template', default=_default_payment_template,
		domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PAYMENT\_%\_document' )]")


