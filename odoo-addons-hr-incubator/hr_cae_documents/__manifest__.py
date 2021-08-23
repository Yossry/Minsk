# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR CAE Documents",
    "summary": """
        * Copies documents from hr_applicant and hr_employee.
        * Adds fields to documents.
    """,
    "author": "Coop IT Easy SCRLfs",
    "website": "https://coopiteasy.be",
    "category": "Human Resources",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["hr_recruitment", "hr_employee_document"],
    "data": ["security/ir.model.access.csv", "views/ir_attachment.xml"],
    "demo": [],
    "installable": True,
    "application": False,
}
