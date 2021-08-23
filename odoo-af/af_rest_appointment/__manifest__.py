# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "AF REST Appointment",
    "version": "12.0.1.0.0",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "category": "Tools",
    "depends": ["af_rest_core", "calendar_af", "partner_employee360", ],
    "external_dependencies": [],
    "data": [
        "views/af_rest_appointment_views.xml",
        "security/ir.model.access.csv",
    ],
    "application": True,
    "installable": True,
}
