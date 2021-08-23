import pdb
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MultiPlayslipDonewizard(models.TransientModel):
	_name = 'multi.payslip.done.wizard'
	_description = 'Confirming the Multiple Payslips Through This Wizard'
	
	@api.model	
	def _get_payslips(self):		
		if self.env.context.get('active_model', False) == 'hr.payslip' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
	
	### cols	
	payslips = fields.Many2many('hr.payslip', 'payslip_multi_done_rel','payslip_id','mutli_done_id', string='Payslip', required=True, default=_get_payslips)
	
	
	@api.multi
	def process_payslips(self):
		for rec in self:
			if rec.payslips:
				for slip in rec.payslips:
					if slip.state !='done':
						_logger.info('.......Payslip No %r is being process. ..............', slip.number)
						slip.process_sheet()
		
		return {'type': 'ir.actions.act_window_close'}
	
