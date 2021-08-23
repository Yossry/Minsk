# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Employees for School",
    "version": "12.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "hr",
        "contacts_school",
        "education",
        "base_month",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Human Resources",
    "data": [
        "security/hr_school_rules.xml",
        "views/res_partner_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_supervised_year_view.xml",
        "views/education_order_day_view.xml",
        "security/ir.model.access.csv",
        "security/hr_school_security.xml",
    ],
    "installable": True,
}
