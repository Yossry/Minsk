import pdb
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class invoice_checked(models.TransientModel):
	_name ='invoice.checked'
	_description = 'Check Invoices'

	invoice_ids = fields.Many2many('account.invoice', string='Invoices', default=lambda self: self._context.get('active_ids', False), help="""Only selected Invoices will be Checked.""")                                    				
	    
	@api.multi
	def invoice_checked(self):
		for rec in self.invoice_ids:
			if rec.state == 'draft':
				rec.write({'state' :'checked','checked_by' : self.env.user.id})
		return {'type': 'ir.actions.act_window_close'}


class invoice_approved(models.TransientModel):
	_name ='invoice.approved'
	_description = 'Approve Invoices'

	invoice_ids = fields.Many2many('account.invoice', string='Invoices', default=lambda self: self._context.get('active_ids', False), help="""Only selected Invoices will be Approved.""")                                  				

	@api.multi
	def invoice_approved(self):				
		for rec in self.invoice_ids:
			if rec.state == 'checked':
				rec.action_invoice_open()
				#rec.signal_workflow('invoice_open')
		return {'type': 'ir.actions.act_window_close'}


class invoice_recompute(models.TransientModel):
	_name ='invoice.recompute'
	_description = 'Recompute Invoices'
				
	invoice_ids = fields.Many2many('account.invoice', string='Invoices', default=lambda self: self._context.get('active_ids', False), help="""Only selected Invoices will be Re-Computed.""")                                    				
	
	@api.multi
	def invoice_recompute(self):
		for rec in self.invoice_ids:
			if rec.invoice_type == 'days':
				rec.invoice_type =  'hours'
				rec.invoice_type = 'days'
		return {'type': 'ir.actions.act_window_close'}


