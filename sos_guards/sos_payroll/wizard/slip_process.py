import pdb
import time
import datetime
from odoo import api, fields, models

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class slip_process(models.TransientModel):
	_name ='slip.process'
	_description = 'Slip Process Wizard'
				
	@api.model	
	def _get_slip_ids(self):
		if self._context.get('active_model', False) == 'guards.payslip' and self._context.get('active_ids', False):
			return context['active_ids']
		
	slip_ids = fields.Many2many('guards.payslip', string='Slips', help="""Only selected Slips will be Processed.""",default=_get_slip_ids)

	def slip_processed(self):				
		slip_obj = self.pool.get('guards.payslip')
		        		
		if self.slip_ids:
			slip_obj.guards_process_sheet(self.slip_ids)
				
		return {'type': 'ir.actions.act_window_close'}




