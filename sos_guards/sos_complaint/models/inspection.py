import pdb
import datetime
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo import SUPERUSER_ID


class SOSInspectionGuards(models.Model):
	_name = "sos.inspection.guards"
	_description = "Inspection Guards"

	inspection_id = fields.Many2one('sos.inspection','Inspection')
	name = fields.Char('Name', size=64)
	fathername = fields.Char('Father Name', size=64)
	guard_status = fields.Selection( [ ('armed','Armed'),('civil','Civil')],'Guard Status')
	cnic = fields.Char('CNIC', size=32, index=True)
	contact_no = fields.Char('Contact No.', size=24)
	salary_rate = fields.Integer('Salary Rate')
	last_working_days = fields.Integer('Last Working Days', size=8)
	last_salary = fields.Integer('Last Month Received Salary')
	uniform = fields.Integer('Uniform')
	shoes = fields.Integer('Shoes')
	cap = fields.Integer('Caps')
	belt = fields.Integer('Belt')
	issuance_date = fields.Date('Issuance Date')
	size = fields.Integer('Size')


class SOSInspectionWeapon(models.Model):
	_name = "sos.inspection.weapon"
	_description = "Inspection Weapons"

	inspection_id = fields.Many2one('sos.inspection','Inspection')
	weapon_type = fields.Char('Weapon Type', size=32)
	weapon_serial = fields.Char('Weapon Serial', size=32)
	weapon_license = fields.Char('Weapon License', size=32)
	issuance_date = fields.Date('Issuance Date')
	issued_from = fields.Char('Issued From', size=32)
	weapon_condition = fields.Selection( [ ('ok','Ok'),('need','Need Repair'),('change','To be Changed')],'Weapon Condition')
	

class SOSInspectionAmmunation(models.Model):
	_name = "sos.inspection.ammunation"
	_description = "Inspection Ammunation"

	inspection_id = fields.Many2one('sos.inspection','Inspection')
	rounds_issued = fields.Integer('Rounds Issued')
	rounds_held = fields.Integer('Rounds Held')
	rounds_required = fields.Integer('Rounds Required')
	rounds_condition = fields.Char('Rounds Condition',size=24)
	spare_magazine = fields.Integer('Spare Magazine')
	belt = fields.Integer('Belt/ Pouch')


class SOSInspection(models.Model):
	_name = "sos.inspection"
	_description = "Inspection"

	center_id = fields.Many2one('sos.center','Center',required=True)
	project_id = fields.Many2one('sos.project','Project',required=True)
	post_id = fields.Many2one('sos.post','Post',required=True)
	inspection_date = fields.Date('Inspection Date', required=True)
	employee_ids = fields.One2many('sos.inspection.guards', 'inspection_id', 'Guards')
	weapon_ids = fields.One2many('sos.inspection.weapon', 'inspection_id', 'Weapons')
	ammunation_ids = fields.One2many('sos.inspection.ammunation', 'inspection_id', 'Ammunation')