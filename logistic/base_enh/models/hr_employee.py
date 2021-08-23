# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Travels(models.Model):
    _name = 'travels'
    _description = "Travels"
    
    country_from_id = fields.Many2one('res.country','From',required=True)
    country_to_id = fields.Many2one('res.country','To',required=True)
    date_of_departure = fields.Date()
    date_of_arrival = fields.Date()
    reason = fields.Text()
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    
class DiseasesMedications(models.Model):
    _name = 'diseases.medications'
    _description = "DiseasesMedications"
    
    diseases = fields.Char(required=True)
    medications = fields.Char()
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = "HrEmployee"
    
    social_security_no = fields.Char('Social Security No')
    tax_registration_no = fields.Char('Tax Registration No')
    health_care_insurance_no = fields.Char('Health Care Insurance No')
    national_id_card_no = fields.Char('National ID Card No')
    national_register_no = fields.Char('National Register No')
    diseases_medications = fields.Char('List of diseases & Medications')
    has_us_citizenship = fields.Boolean('Do You Have U.S. citizenship')
    has_diseases = fields.Boolean('Do you Have Chronic Diseases and /or Infectious Diseases')
    travels_ids = fields.One2many('travels','employee_id')
    diseases_medications_ids = fields.One2many('diseases.medications','employee_id')
    