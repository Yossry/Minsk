from odoo import api, fields, models

class hr_payroll_add(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    
    add_other = fields.Boolean('Add Other Allowances/Deductions')
    other_deductions = fields.Float('Other Deductions')
    other_allowances = fields.Float('Other Allowances')

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
        
    trans_allow = fields.Float('Transportation Allowance')
    housing_allow = fields.Float('Housing Allowance')
    live_allow = fields.Float('A high cost of living allowance')
    risk_allow = fields.Float('Risk Allowance')
    other_allowances = fields.Float('Other Allowances')
    other_dedcutions = fields.Float('Other Dedcutions')
    calc_gosi = fields.Boolean('Calculate GOSI')
    gosi = fields.Float('Employee GOSI')
    nationality = fields.Many2one('res.country','Nationality')
    
    @api.onchange('employee_id')
    def onchange_employee_id_nat(self):
        self.nationality = self.employee_id.country_id 
    
    @api.onchange('calc_gosi')
    def onchange_gosi(self):
        if self.nationality.name == 'Saudi Arabia':
            if self.calc_gosi == True:
                if self.wage >= 45000:
                    self.gosi = 45000 * 0.10
                else:
                    self.gosi = (self.wage+self.housing_allow+self.trans_allow+self.live_allow)*0.10
        else:self.gosi = 0.0