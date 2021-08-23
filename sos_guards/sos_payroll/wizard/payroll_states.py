import pdb
import time
import datetime
from odoo import tools
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo import netsvc

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class guards_payslip_approved(models.TransientModel):
	_name ='guards.payslip.approved'
	_description = 'This Wizard will Change the Payslip into Approved Status.'
				
	@api.model	
	def _get_slip_ids(self):
		res = False
		if self._context.get('active_model', False) == 'guards.payslip' and self._context.get('active_ids', False):
			return self._context['active_ids']
		
	slip_ids = fields.Many2many('guards.payslip', string='Pay Slips', default=_get_slip_ids, help="""Only selected Payslips will be Approved.""")                                   				

	@api.multi
	def slip_approved(self):				
		for slip in self.slip_ids:
			slip.guards_verify_sheet()
			slip.guards_process_sheet()
			
		return {'type': 'ir.actions.act_window_close'}




