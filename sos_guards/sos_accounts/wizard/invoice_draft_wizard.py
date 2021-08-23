import pdb
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SOSInvoiceDraftwizard(models.TransientModel):
	_name = 'sos.invoice.draft.wizard'
	_description = 'Invoices Draft Wizard'
	
	@api.model
	def _get_invoice_id(self):
		inv_id = self.env['account.invoice'].browse(self._context.get('active_id',False))
		if inv_id:
			return inv_id.id
		return True	
	
	### cols	
	invoice_id = fields.Many2one('account.invoice', 'Invoice', required=True, default=_get_invoice_id)
	
	@api.one
	def invoice_status(self):
		if self.env.user.id in (1,125,10):
			invoice_id = self.invoice_id or False
			
			if invoice_id and invoice_id.move_id and invoice_id.state == 'open':
				move_id = invoice_id.move_id
				invoice_id.move_id = False
				invoice_id.state='draft'
				self.env.cr.execute("delete from account_move where id=%s"%(move_id.id))
					
				# Workflow Setting
				#self.env.cr.execute("select id as inst_id from wkf_instance where wkf_id=1 and res_id=%s"%(invoice_id.id))
				#inst_id = self.env.cr.dictfetchall()[0]['inst_id']
				#self.env.cr.execute("update wkf_workitem set act_id = 1, state='active' where inst_id=%s"%(inst_id))
			
			else:
				raise UserError(_('No Move Entry For this Invoice or Not in Approved State'))	
		else:
			raise UserError(_('You are not Authorized to do this! Please Contact To System Administrator'))		
		return {'type': 'ir.actions.act_window_close'}
	
