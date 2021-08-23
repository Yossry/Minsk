import pdb
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class InvoiceAccountingDatewizard(models.TransientModel):
	_name = 'invoice.accounting.date.wizard'
	_description = 'Invoice Accounting Date Wizard'
	
	@api.model
	def _get_invoice_id(self):
		inv_id = self.env['account.invoice'].browse(self._context.get('active_id',False))
		if inv_id:
			return inv_id.id
		return True	
	
	### cols	
	invoice_id = fields.Many2one('account.invoice', 'Invoice', required=True, default=_get_invoice_id)
	date_invoice = fields.Date('Invoice Accounting Date')
	date_from = fields.Date('From Date')
	date_to = fields.Date('To Date')
	
	
	@api.one
	def change_date(self):
		if self.env.user.id in [1,5,44]:
			invoice_id = self.invoice_id or False
			
			#To Change the Invoice Accounting Date
			if self.date_invoice:
				if invoice_id and invoice_id.move_id:
					for line in invoice_id.move_id.line_ids:
						#Change Move Line Date
						self.env.cr.execute("update account_move_line set date = %s where id=%s", (self.date_invoice,line.id))
					# Change Move Date	
					self.env.cr.execute("update account_move set date = %s where id=%s", (self.date_invoice,invoice_id.move_id.id))
					#Change Invoice Accounting Date
					self.env.cr.execute("update account_invoice set date_invoice = %s where id=%s", (self.date_invoice,invoice_id.id))
					msg = "Invoice Accounting Date has been Changed to " + self.date_invoice + " By the User " + self.env.user.name
					invoice_id.message_post(msg)
				else:
					raise UserError(_('No Invoice Selected. OR Date Not Entered'))
			
			# To Change Invoice Date From
			if self.date_from:
				invoice_id.date_from = self.date_from
				msg = "Invoice Date From has been Changed to " + self.date_from + " By the User " + self.env.user.name
				invoice_id.message_post(msg)
			
			# To Change the Invoiec Date To
			if self.date_to:
				invoice_id.date_to = self.date_to
				msg = "Invoice Date To has been Changed to " + self.date_to + " By the User " + self.env.user.name
				invoice_id.message_post(msg)	
		else:
			raise UserError(_('You are not Authorized to do this! Please Contact To System Administrator'))		
		return {'type': 'ir.actions.act_window_close'}
	
