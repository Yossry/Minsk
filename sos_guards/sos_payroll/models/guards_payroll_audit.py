from calendar import isleap
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
import odoo.addons.decimal_precision as dp
DATETIME_FORMAT = "%Y-%m-%d"


class GuardsPayslipAudit(models.Model):
	_name = 'guards.payslip.audit'
	_description = 'Payslip Audit Entries'
	_order = 'id desc'
		
	center_id = fields.Many2one('sos.center','Center', required=True, readonly=True, states={'draft': [('readonly', False)]})
	project_id = fields.Many2one('sos.project','Project', required=True, readonly=True, states={'draft': [('readonly', False)]})	
	post_id = fields.Many2one('sos.post','Post', required=True, readonly=True, states={'draft': [('readonly', False)]})	
	note = fields.Text('Note', required=True, readonly=True, states={'draft': [('readonly', False)]})
	diff = fields.Integer('Difference',help='''If there are 93 Days Invoice and 124 Days Attendance, and Arrear Invoice have to be generated then enter -31 here 
				\n If there are 93 Days Invoice and 91 Days Attendance, and there is 2 Days shortfall, then enter 2 here''', required=True, readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('error', 'Error'), ('done', 'Done')],'Status',readonly=True, default='draft')