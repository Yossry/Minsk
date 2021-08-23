# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Calendar AF",
    "version": "12.0.1.0.1",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "category": "Tools",
    "depends": ["calendar", "partner_view_360" ],
    "external_dependencies": [
        # "service_identity",
        # "stompest",
        # "stompest.async",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/res_users_view.xml",
        "views/calendar_af_view.xml",
        "views/calendar_schedule_view.xml",
        "views/calendar_appointment_view.xml",
        "views/calendar_occasion_view.xml",
        "views/calendar_channel_view.xml",
        "views/calendar_appointment_type_view.xml",
        "views/calendar_mapped_dates_view.xml",
        "security/ir.model.access.csv",
        "data/calendar.channel.csv",
        "data/calendar.appointment.type.csv",
    ],
    "application": True,
    "installable": True,
}
