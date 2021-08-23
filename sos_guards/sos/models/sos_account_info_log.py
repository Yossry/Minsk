import pdb
from datetime import datetime
from odoo import api, fields, models


class SOSAccountLog(models.Model):
	_name = "sos.account.info.log"
	_inherit = ['mail.thread']
	_description = "Guards Account Info Log"
	_order = 'id desc'

	name = fields.Char('Name')
	employee_id = fields.Many2one('hr.employee','Employee')
	code = fields.Char('Code')
	resigdate = fields.Date('Resignation Date')
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	bank_id = fields.Many2one('sos.bank','Bank Name')
	bankacctitle = fields.Char('Account Title', size=64 ,track_visibility='onchange')
	bankacc = fields.Char('Account No', size=32, track_visibility='onchange')
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner')
	branch =  fields.Char('Branch', size=64)
	acc_creation_date = fields.Date('Creation Date')	
