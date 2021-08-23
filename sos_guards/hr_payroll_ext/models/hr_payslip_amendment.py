
from odoo.tools.translate import _
from odoo import models, fields, api


class hr_payslip_amendment(models.Model):
	_name = 'hr.payslip.amendment'
	_description = 'Pay Slip Amendment'
	_inherit = ['mail.thread']

	name= fields.Char('Description',size=128,required=True,readonly=True,states={'draft': [('readonly', False)]},)
	input_id = fields.Many2one('hr.rule.input','Salary Rule Input',required=True,readonly=True,states={'draft': [('readonly', False)]},)
	employee_id = fields.Many2one('hr.employee','Employee',required=True,readonly=True,states={'draft': [('readonly', False)]},)
	amount =  fields.Float('Amount',required=True,readonly=True,states={'draft': [('readonly', False)]},help="The meaning of this field is dependant on the salary rule that uses it.")
	state = fields.Selection([('draft', 'Draft'),('validate', 'Confirmed'),('cancel', 'Cancelled'),('done', 'Done'),],'State',required=True,readonly=True,default='draft')
	note = fields.Text('Memo')
	

#	def onchange_employee(self, cr, uid, ids, employee_id, context=None):
#
#		if not employee_id:
#			return {}
#		ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
#		name = _('Pay Slip Amendment: %s (%s)') % (ee.name, ee.employee_no)
#		val = {'name': name}
#		return {'value': val}
#
#	def unlink(self, cr, uid, ids, context=None):
#
#		for psa in self.browse(cr, uid, ids, context=context):
#			if psa.state in ['validate', 'done']:
#				raise orm.except_orm(_('Invalid Action'),_('A Pay Slip Amendment that has been confirmed cannot be deleted!'))
#
#		return super(hr_payslip_amendment, self).unlink(cr, uid, ids, context=context)#
