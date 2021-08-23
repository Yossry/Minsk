
from num2words import num2words
from odoo import models, fields, api, _

class GeneralEntryTemplates(models.Model):
	_inherit=["account.move"]
	
	jv_style = fields.Many2one('report.template.settings', 'Journal Entry Style', help="Select Style to use when printing this Journal Entry", default= 1)	
	
	
