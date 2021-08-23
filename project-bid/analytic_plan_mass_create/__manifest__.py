# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Analytic Plan Mass Create",
    "version": "12.0.1.0.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "summary": """Analytic Plan Mass Create""",
    "license": "AGPL-3",
    "depends": [
        "analytic_plan",
        "account"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/analytic_plan_mass_create_template_view.xml",
        "wizard/analytic_plan_mass_create_view.xml"
    ],
    'installable': True,
}
