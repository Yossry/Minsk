import pdb
from datetime import datetime
from odoo import api, fields, models, _
	

class res_partner(models.Model):
	_inherit = "res.partner"
	_order = 'name'

	post_id = fields.Many2one('sos.post', 'Post Info', ondelete='cascade')
	code = fields.Char('Code')


class res_partner_bank(models.Model):
	_name = "res.partner.bank"	
	_inherit = "res.partner.bank"	
	
	open_date = fields.Date('Opening Date')
	signatury_name = fields.Char('Signatury Name', size=64)
	signatury_designation = fields.Char('Signatury Designation', size=64)






