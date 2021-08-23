import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class sos_fiscalyear(models.Model):
	_name = "sos.fiscalyear"
	_description = "Fiscal Year"
	_order = "date_start, id"
	
	name = fields.Char('Fiscal Year', required=True)
	code = fields.Char('Code', size=6, required=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id.id)
	date_start = fields.Date('Start Date', required=True)
	date_stop = fields.Date('End Date', required=True)
	period_ids = fields.One2many('sos.period', 'fiscalyear_id', 'Periods')
	state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', default='draft', readonly=True, copy=False)		
	
	@api.one
	@api.constrains('date_start', 'date_stop')
	def _check_duration(self):
		if self.date_stop < self.date_start:
			raise ValueError(_('Error!\nThe start date of a fiscal year must precede its end date.'))
		return True
		
	
	@api.one
	def create_period3(self):
		interval = 3
		fy = self
		period_obj = self.env['sos.period']
		
		ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
		while ds.strftime('%Y-%m-%d') < fy.date_stop:
			de = ds + relativedelta(months=interval, days=-1)

			if de.strftime('%Y-%m-%d') > fy.date_stop:
				de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

			period_obj.create({
				'name': ds.strftime('%m/%Y'),
				'code': ds.strftime('%m/%Y'),
				'date_start': ds.strftime('%Y-%m-%d'),
				'date_stop': de.strftime('%Y-%m-%d'),
				'fiscalyear_id': fy.id,
			})
			ds = ds + relativedelta(months=interval)
		return True

	@api.one
	def create_period(self):
		interval = 1
		fy = self
		period_obj = self.env['sos.period']
		
		ds = fy.date_start
		while ds < fy.date_stop:
			de = ds + relativedelta(months=interval, days=-1)

			if de > fy.date_stop:
				de = fy.date_stop

			period_obj.create({
				'name': ds.strftime('%m/%Y'),
				'code': ds.strftime('%m/%Y'),
				'date_start': ds.strftime('%Y-%m-%d'),
				'date_stop': de.strftime('%Y-%m-%d'),
				'fiscalyear_id': fy.id,
			})
			ds = ds + relativedelta(months=interval)
		return True
	
	
	@api.one
	def find(self, dt=None, exception=True):
		res = self.finds(dt, exception)
		return res and res[0] or False
	
	@api.one
	def finds(self, dt=None, exception=True):
		context = self._context or {}
		dt = dt
		if not dt:
			dt = fields.date.context_today(self)
		args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
		if context.get('company_id', False):
			company_id = context['company_id']
		else:
			company_id = self.env.user.company_id.id
		args.append(('company_id', '=', company_id))
		ids = self.search(args)
		
		if not ids:
			if exception:
				model, action_id = self.env['ir.model.data'].get_object_reference('sos', 'action_sos_fiscalyear')
				msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods and configure a fiscal year.') % dt
				raise ValidationError(_('Go to the configuration panel'))
			else:
				return []
		return ids
	
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=80):
		args = args or []
		if operator in expression.NEGATIVE_TERM_OPERATORS:
			domain = [('code', operator, name), ('name', operator, name)]
		else:
			domain = ['|', ('code', operator, name), ('name', operator, name)]
		ids = self.search(expression.AND([domain, args]), limit=limit)
		return self.name_get()


class sos_period(models.Model):
	_name = "sos.period"
	_description = "SOS period"
	_order = "date_start, special desc"
	
	name = fields.Char('Period Name', required=True)
	code = fields.Char('Code', size=12)
	special = fields.Boolean('Opening/Closing Period',help="These periods can overlap.")
	date_start = fields.Date('Start of Period', required=True, states={'done':[('readonly',True)]})
	date_stop = fields.Date('End of Period', required=True, states={'done':[('readonly',True)]})
	fiscalyear_id = fields.Many2one('sos.fiscalyear', 'Fiscal Year', required=True, states={'done':[('readonly',True)]})
	company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='Company', store=True, readonly=True)
	state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', default='draft', readonly=True, copy=False,
								help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
	
	_sql_constraints = [
		('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
	]

	@api.one
	@api.constrains('date_start', 'date_stop')
	def _check_duration(self):
		if self.date_stop < self.date_start:
			raise ValueError(_('Error!\nThe start date of a fiscal year must precede its end date.'))
		return True
	
	@api.multi
	@api.constrains('date_stop')
	def _check_year_limit(self):
		for obj_period in self:
			if obj_period.special:
				continue

			if obj_period.fiscalyear_id.date_stop < obj_period.date_stop or \
			   obj_period.fiscalyear_id.date_stop < obj_period.date_start or \
			   obj_period.fiscalyear_id.date_start > obj_period.date_start or \
			   obj_period.fiscalyear_id.date_start > obj_period.date_stop:
				raise ValueError(_('Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.'))

			pids = obj_period.search([('date_stop','>=',obj_period.date_start),('date_start','<=',obj_period.date_stop),('special','=',False),('id','<>',obj_period.id)])
			for period in pids:
				if period.fiscalyear_id.company_id.id == obj_period.fiscalyear_id.company_id.id:
					return False
		return True

	@api.returns('self')
	def next(self, period, step):
		ids = self.search([('date_start','>',period.date_start)])
		if len(ids)>=step:
			return ids[step-1]
		return False

	@api.returns('self')
	def find(self, dt=None, context=None):
		context = self._context or {}
		if not dt:
			dt = fields.date.context_today(self)
		args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
		if context.get('company_id', False):
			args.append(('company_id', '=', context['company_id']))
		else:
			company_id = self.env.user.company_id.id
			args.append(('company_id', '=', company_id))
		result = []
		if context.get('sos_period_prefer_normal', True):
			# look for non-special periods first, and fallback to all if no result is found
			result = self.search(args + [('special', '=', False)])
		if not result:
			result = self.search(args)
		if not result:
			model, action_id = self.env['ir.model.data'].get_object_reference('sos', 'action_sos_period')
			msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt
			raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
		return result

	@api.multi
	def action_draft(self):
		mode = 'draft'
		for period in self:
			if period.fiscalyear_id.state == 'done':
				raise Warning(_('Warning!'), _('You can not re-open a period which belongs to closed fiscal year'))
		self.env.cr.execute('update sos_period set state=%s where id in %s', (mode, tuple(ids),))
		self.invalidate_cache()
		return True
	
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if operator in expression.NEGATIVE_TERM_OPERATORS:
			domain = [('code', operator, name), ('name', operator, name)]
		else:
			domain = ['|', ('code', operator, name), ('name', operator, name)]
		ids = self.search(expression.AND([domain, args]), limit=limit)
		return self.name_get()
	
	@api.one
	def build_ctx_periods(self, period_from_id, period_to_id):
		if period_from_id == period_to_id:
			return [period_from_id]
		period_from = self.browse(period_from_id)
		period_date_start = period_from.date_start
		company1_id = period_from.company_id.id
		period_to = self.browse(period_to_id)
		period_date_stop = period_to.date_stop
		company2_id = period_to.company_id.id
		if company1_id != company2_id:
			raise UserError(_('You should choose the periods that belong to the same company.'))
		if period_date_start > period_date_stop:
			raise UserError(_('Start period should precede then end period.'))
			
			
		if period_from.special:
			return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop)])
		return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop), ('special', '=', False)])


