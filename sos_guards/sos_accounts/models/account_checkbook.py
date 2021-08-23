from odoo import fields, models, api, _
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class AccountCheckbook(models.Model):
	_name = 'account.checkbook'
	_description = 'Account Checkbook'

	name = fields.Char('Name', help="Cheque Book Name...")
	start_number = fields.Integer('Start Number',readonly=True,states={'draft': [('readonly', False)]},)
	end_number = fields.Integer('End Number',readonly=True,states={'draft': [('readonly', False)]},)
	check_ids = fields.One2many('account.checkbook.line','checkbook_id',string='Checks',readonly=True,)
	state = fields.Selection([('draft', 'Draft'), ('active', 'In Use'), ('used', 'Used')],string='State',default='draft',copy=False)
	date = fields.Date('Date',required=False,readonly=True,states={'draft': [('readonly', False)]},default=fields.Date.context_today,)
	block_manual_number = fields.Boolean(readonly=True,default=True,string='Block manual number?',states={'draft': [('readonly', False)]},help='Block user to enter manually another number than the suggested')
			
	@api.one
	def create_cheque_entries(self):
		line_obj = self.env['account.checkbook.line']
		if self.start_number <= self.end_number:		
			for a in range (self.start_number,self.end_number):
				vals = {
					'name' : "Cheque#:" + str(a),
					'checkbook_id' : self.id,
					'check_number' : a,
					'description' : '',
					'state' : 'draft',
					}
				line_obj.sudo().create(vals)
			self.state = 'active'		
		return True		 	
	
	@api.multi
	def _compute_name(self):
		for rec in self:
			if rec.issue_check_subtype == 'deferred':
				name = _('Deferred Checks')
			else:
				name = _('Currents Checks')
			if rec.range_to:
				name += _(' up to %s') % rec.range_to
			rec.name = name

	@api.one
	def unlink(self):
		if self.issue_check_ids:
			raise ValidationError(_('You can drop a checkbook if it has been used on checks!'))
		return super(AccountCheckbook, self).unlink()

					
class AccountCheckbookLine(models.Model):
	_name = 'account.checkbook.line'
	_description = 'Account Checkbook Line'
	
	name = fields.Char()
	checkbook_id = fields.Many2one('account.checkbook','Checkbook',readonly=True,states={'draft': [('readonly', False)]},)
	check_number = fields.Char('Check Number')
	used_date = fields.Date('Used Date')
	description = fields.Char()
	state = fields.Selection([('draft', 'Draft'), ('active', 'In Use'), ('used', 'Used')],string='State',default='draft',copy=False)
