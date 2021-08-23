from datetime import datetime
from odoo.tools.translate import _
from odoo import models, fields, api


class hr_payroll_run(models.Model):
	_inherit = 'hr.payslip.run'

	register_id = fields.Many2one('hr.payroll.register', 'Register')
	

class hr_payroll_register(models.Model):
	_name = 'hr.payroll.register'
	_description = 'HR Payroll Register'

	@api.model	
	def _get_default_name(self):
		nMonth = datetime.now().strftime('%B')
		year = datetime.now().year
		name = _('Payroll for the Month of %s %s' % (nMonth, year))
		return name

	name = fields.Char('Description', size=256,default=_get_default_name)
	state = fields.Selection([('draft', 'Draft'),('close', 'Close'),], 'Status', index=True, readonly=True,default='draft')
	date_start = fields.Datetime('Date From', required=True, readonly=True,states={'draft': [('readonly', False)]})
	date_end = fields.Datetime('Date To', required=True, readonly=True,states={'draft': [('readonly', False)]})
	run_ids = fields.One2many('hr.payslip.run', 'register_id', readonly=True,states={'draft': [('readonly', False)]})
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id)
	
	_sql_constraints = [('unique_name', 'UNIQUE(name)', _('Payroll Register description must be unique.')),]

	@api.multi
	def action_delete_runs(self):		
		for run in self.run_ids:
			run.slip_ids.unlink()
			run.unlink()
		self.unlink()
		

