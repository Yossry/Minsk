# -*- coding: utf-8 -*-
import math
from odoo import models, fields, api
from datetime import datetime
import odoo.addons.decimal_precision as dp
from operator import le
from _ast import If

class SocialSecYear(models.Model):
    _name = 'social.year'
    
    name = fields.Integer('Year')
    emp_perc = fields.Float('Employee Percentage')
    comp_perc = fields.Float('Company Percentage')
    
class Insurance_comp(models.Model):
    _name = 'insurance.comp'
    
    name = fields.Char('Insurance company name')
    emp_perc = fields.Float('Employee Percentage')
    comp_perc = fields.Float('Company Percentage')
    total = fields.Float('Insurance Offer yearly amount')

class empIncomeTaxCalc(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    income_emp_tax = fields.Float('Income Tax Amount')
    f_5 = fields.Float('1-5')
    s_5 = fields.Float('1-5')
    t_5 = fields.Float('1-5')
    f_5 = fields.Float('1-5')
    legal_exemption = fields.Float('Legal Exemption')
    taxable_wage = fields.Float('Taxable Income')
    income1 = fields.Float('Income 1')
    income2 = fields.Float('Income 2')
    income3 = fields.Float('Income 3')
    income4 = fields.Float('Income 4')
    yearly_income_taxes = fields.Float('Yearly Income Tax')
    monthly_income_taxes = fields.Float('Monthly Income Tax')
    zez = fields.Float('zez')
    employee_social = fields.Float('Employee Social Security')
    company_social = fields.Float('Company Social Security')
    company_insurance  = fields.Float('Company Health Insurance')
    employee_insurance = fields.Float('Employee Health Insurance (Monthly)')
    social_year = fields.Many2one('social.year','Social security year')
    insurance_comp = fields.Many2one('insurance.comp','Insurance Company (Monthly)')
    no_of_persons = fields.Integer('No of family members')
    family_perc = fields.Float('Persons Percentage')
    
    @api.onchange('social_year')
    def onchange_social(self):
        if self.wage:
            self.employee_social = self.wage * self.social_year.emp_perc
            self.company_social = self.wage * self.social_year.comp_perc
    
    @api.onchange('insurance_comp')
    def onchange_insurance(self):
        if self.no_of_persons > 0:
            self.employee_insurance = ((self.insurance_comp.emp_perc*self.insurance_comp.total)/12) + (((self.insurance_comp.total*self.family_perc)*self.no_of_persons)/12)  
            self.company_insurance = (self.insurance_comp.total * self.insurance_comp.comp_perc)/12
        else:
            self.employee_insurance = (self.insurance_comp.emp_perc*self.insurance_comp.total)/12
            self.company_insurance = (self.insurance_comp.total * self.insurance_comp.comp_perc)/12
    
    @api.onchange('wage')
    def comp_taxableIncome(self):
        if self.wage:
            self.taxable_wage = self.wage * 12
    
    @api.onchange('taxable_wage')
    def onchange_TaxableWage(self):
        if  self.taxable_wage:
            if self.employee_id.marital == 'single':
                self.legal_exemption = self.taxable_wage - 9000
                if self.legal_exemption < 0.0:
                    self.legal_exemption = 0.0
            if self.employee_id.marital == 'married':
                self.legal_exemption = self.taxable_wage - 18000
                if self.legal_exemption < 0.0:
                    self.legal_exemption = 0.0
    
    @api.onchange('legal_exemption')
    def onchange_T(self):
        if self.legal_exemption > 0.0:
            self.f_5 = 5000
            self.s_5 = 10000
            self.t_5 = 15000
            self.f_5 = 20000
            self.zez = 0.0
            
            if self.legal_exemption >= 5000.0: 
                self.income1 = 5000 * 0.05 # 1
            else: self.income1 = self.legal_exemption * 0.05
            
            if (self.legal_exemption - 5000.0) >= 5000.0:
                 self.income2 = 5000.0 * 0.1 #2
            else: self.income2 = (self.legal_exemption - 5000.0) * 0.1
            
            if (self.legal_exemption - 10000.0) >= 5000:
                self.income3 = 5000.0 * 0.15
            else: self.income3 = (self.legal_exemption - 10000) * 0.15
            
            if (self.legal_exemption - 15000.0) >= 5000.0:
                self.income4 = 5000.0 * 0.2
            else: self.income4 = (self.legal_exemption - 15000.0) *  0.2
            
            if self.income1 < 0.0:
                self.income1 = 0.0
            if self.income2 < 0.0:
                self.income2 = 0.0
            if self.income3 < 0.0:
                self.income3 = 0.0
            if self.income4 < 0.0:
                self.income4 = 0.0
                 
            self.yearly_income_taxes = (self.income1 + self.income2 + self.income3 + self.income4)
            self.monthly_income_taxes = self.yearly_income_taxes / 12
           