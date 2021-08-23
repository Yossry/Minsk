import pdb
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models, _


class invoices_cron_wizard(models.TransientModel):
	_name ='invoices.cron.wizard'
	_description = 'Generate Invoices Cron Entries'

	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])
	project_ids = fields.Many2many('sos.project',string='Filter on Projects', help="Only selected Projects Invoices will be generated.")
	post_ids = fields.Many2many('sos.center', string='Filter on Posts', help="Only selected Posts Salaries will be generated.")
	
	@api.multi
	def generate_cron_entry(self):
		cron_invoices_pool = self.env['invoices.cron']
		post_pool = self.env['sos.post']
	
		for data in self:
			post_domain = []	
			if data.project_ids:
				post_domain.append(('project_id','in', data.project_ids.ids))
			if data.post_ids:
				post_domain.append(('id','in', data.post_ids.ids))
			post_domain.append(('active','=', True))
			
			post_ids = post_pool.search(post_domain)
			for post in post_ids:
				res = {
					'post_id': post.id,
					'date_from': data.date_from,
					'date_to': data.date_to,
					'state': 'draft',
					'center_id': post.center_id.id,
					'project_id': post.project_id and post.project_id.id or False,
				}								
				cron_rec = cron_invoices_pool.sudo().create(res)
		return {'type': 'ir.actions.act_window_close'}