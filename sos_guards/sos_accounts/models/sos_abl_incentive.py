import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import api, fields, models
from odoo import tools
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError


class SOSABLIncentive(models.Model):
	_name = 'sos.abl.incentive'
	_order = 'id desc'
	_description = 'ABL Incentives'
	_inherit = ['mail.thread']

	@api.multi
	@api.depends('line_ids')
	def _get_total(self):
		for rec in self:
			total = 0
			for line in rec.line_ids:
				total = line.amount + total
			rec.total_amount = total
	
	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise UserError('You can not delete record which are not in draft state.')
	
	name = fields.Char('Description',track_visibility='always')	
	project_id = fields.Many2one('sos.project','Project', default=26,track_visibility='always')	
	date = fields.Date('Date', required=True,default=lambda *a: str(datetime.now())[:10],track_visibility='always')
	state = fields.Selection([('draft', 'Draft'),('validate', 'Validate'),('done', 'Done')], 'Status', default='draft',track_visibility='onchange')
	line_ids = fields.One2many('sos.abl.incentive.lines','incentive_id',string='Incentive Lines')
	credit_account_id = fields.Many2one('account.account','Credit Account', default=65,track_visibility='always')
	debit_account_id = fields.Many2one('account.account','Debit Account', default=169,track_visibility='always')
	journal_id = fields.Many2one('account.journal','Journal', default=1,track_visibility='always')
	move_id = 	fields.Many2one('account.move','Move',track_visibility='always')
	total_amount = fields.Float(compute='_get_total',string='Total',store=True)
	received_amount = fields.Float('Received Amount',track_visibility='always')
	note = fields.Text('Note')
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])

	@api.multi
	def incentive_validate(self):
		for rec in self:
			if rec.received_amount == rec.total_amount:
				rec.write({'state':'validate'})
			else:
				raise UserError('Received Amount and Total Amount Does not Match. Please Check it.')

	@api.multi
	def incentive_done(self):
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']
		move_lines=[]
		for rec in self:
			for line in rec.line_ids:
				move_lines.append((0,0,{
					'name': rec.name,
					'debit': line.amount,
					'credit': 0.0,
					'account_id': rec.debit_account_id.id or 65,	#Allied Bank
					'journal_id': 1,  	#Sales Journal
					'date': rec.date,
					'project_id': rec.project_id.id,
					'a5_id': line.partner_id.analytic_code_id.id,
					'd_bin': '0000010000',
				}))

			move_lines.append((0,0,{
				'name': rec.name,
				'debit': 0.0,
				'credit': rec.total_amount,
				'account_id': rec.credit_account_id.id or 169,	#32014 ABL incentives Payable
				'journal_id': 1,  	#Sales Journal
				'date': rec.date,
				'project_id': rec.project_id.id,
			}))

			move = {
				'ref': 'ABL Incenvtive-' + str(rec.id),
				'name': rec.name,
				'journal_id': rec.journal_id.id or 1,  # Stock Journal
				'date': rec.date,
				'narration': rec.name + ":Incentives:" + rec.date,
				'state': 'posted',
				'line_ids': move_lines,
			}
			move_id = move_obj.sudo().create(move)
			rec.write({'state':'done','move_id':move_id.id})

	
class SOSABLIncentiveLines(models.Model):
	_name = 'sos.abl.incentive.lines'
	_order = 'id desc'
	_description = 'ABL Incentives Lines'
			
	post_id = fields.Many2one('sos.post','Post')
	partner_id = fields.Many2one('res.partner',string='Post Ref.',related='post_id.partner_id')
	incentive_id = fields.Many2one('sos.abl.incentive','Incentive')
	amount = fields.Float('Amount')	
	
	



		
		
		



