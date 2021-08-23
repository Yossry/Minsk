# -*- encoding: utf-8 -*-
{
    'name' : 'RL - Jordan Payroll',
    'version' : '12.0.1',
    'category' : 'Human Resources',
    'author' : 'Royal Line for Shipping Services',
    'website' : 'www.royalline.gold',
    'license' : 'AGPL-3',
    'summary' : 'Manage Payroll Of Jordan',
    'description': """
        - In contract :
            - New field 'Salary Increase': if employee salary raised during the year not in the first two months of the year, then the social security will be deduct from old salary until the first of January of the next year. The amount of this field will be added to the wage [Basic Salary] automatically at the first of January.
            - New salary rules:
                - Salary Increase Allowance.
                - Salary Increase Deduction.
                - Social security deduction.
                - Social security contribution.
                - Income tax.""",
    'data': [
            'view/hr_contract.xml',
            'view/salary_rule.xml',
             ],
    'depends' : ['base' ,'hr_payroll'],
    'installable': True,
    'auto_install': False,
}