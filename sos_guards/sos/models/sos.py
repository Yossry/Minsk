import pdb
from odoo import api, fields, models, _


class SOSEducation(models.Model):
	_name = "sos.education"
	_description = "SOS Education"
	
	name = fields.Char('Education', size=64)        
	guard_ids = fields.One2many('hr.guard', 'education_id', 'Guard')


class SOSBank(models.Model):
	_name = "sos.bank"
	_description = "SOS Bank"

	name = fields.Char('Bank Name', size=64, required=True)
	account = fields.Char('Account', size=32)
	guard_ids = fields.One2many('hr.guard', 'bank_id', 'Guards')


class SOSDesignation(models.Model):
	_name = "sos.designation"
	_description = "SOS Designation"
	
	name = fields.Char('Designation', size=64, required=True)
	guard_ids = fields.One2many('hr.guard', 'designation_id', 'Guards')


class SOSSubCast(models.Model):
	_name = "sos.subcast"
	_description = "SOS SubCast"

	name = fields.Char('SubCast', size=64, required=True)
	cast_id = fields.Many2one('sos.cast', 'Cast', required=True)
	guard_ids = fields.One2many('hr.guard', 'subcast_id', 'Guards')


class SOSCast(models.Model):
	_name = "sos.cast"
	_description = "SOS Cast"

	name = fields.Char('Cast', size=64, required=True)
	subcast_ids = fields.One2many('sos.subcast', 'cast_id', 'SubCasts')
	guard_ids = fields.One2many('hr.guard', 'cast_id', 'Guards')


class SOSReligion(models.Model):
	_name = "sos.religion"
	_description = "SOS Religion"

	name = fields.Char('Religion', size=64, required=True)
	guard_ids = fields.One2many('hr.guard', 'religion_id', 'Guards')


class SOSBloodGroup(models.Model):
	_name = "sos.bloodgroup"
	_description = "SOS Blood Group"

	name = fields.Char('Blood Group', size=64, required=True)
	guard_ids = fields.One2many('hr.guard', 'bloodgroup_id', 'Guards')

	
class SOSCity(models.Model):
	_description = "SOS City"
	_name = 'sos.city'
	_order = 'name'

	name = fields.Char('City Name', size=64, index=True)
	center_id = fields.Many2one('sos.center', string='Center')