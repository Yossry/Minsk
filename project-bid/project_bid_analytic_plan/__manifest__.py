# © 2015-17 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Project Bid Analytic Plan",
    "version": "12.0.1.0.0",
    'license': 'AGPL-3',
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["project_bid", "analytic_plan", "sale_management",
                "analytic_resource_plan"],
    "summary": "Allows to create planning lines from the project bid.",
    "data": [
        "view/project_bid_template_view.xml",
        "view/project_bid_view.xml",
    ],
    'installable': True,
}
