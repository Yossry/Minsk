# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Test Data AF",
    "version": "12.0.1.0.1",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "category": "Tools",
    "depends": [
        "contacts", 
        "hr", 
        "calendar", 
        "partner_view_360", 
        "partner_kpi_data", 
        "res_drivers_license", 
		"res_sni", 
		"res_ssyk", 
		"res_sun", 
		"partner_daily_notes", 
		"partner_desired_jobs",
        "partner_fax",
        "partner_firstname",
        ],
    
    "data": [
        "data/country_state/res.country.state.csv",
        #"data/res.partner.csv", --> Daniels fil
        "data/af_office/res.partner.csv", 
		"data/organisationer/res.partner.csv",
		"data/arbetsg_organisation/res.partner.csv",
        "data/arbetsg/res.partner.csv", 
		"data/arbetsg_2adr/res.partner.csv", 
		#"data/arbetsg_utl_adr/res.partner.csv", #--> mapp finns inte
		"data/arbetsg_cct/res.partner.csv",
		"data/user_cct/res.partner.csv", #--> fungerar inte med mer än ~10st av någon anledning
		"data/arbetsg/res.partner.kpi.csv",
		"data/arbetsg_sni1/res.sni.csv",
		#"data/arbetsg_sni2/res_sni.csv",
        "data/arbetsg/res.ssyk.csv",
		"data/arbetsg/res.partner.jobs.csv", 
		"data/arbetsg/res.partner.note.type.csv",
        "data/arbetsg/res.partner.notes.csv",
		"data/arbetsg_lst_cnt/res.partner.notes.csv",
		"data/res_users.xml", 
        "data/arbetsg_hr_imp1/hr.employee.csv", 
		#"data/arbetsg_hr_imp2/hr_employee.csv",
    ],
    "application": False,
    "installable": True,
}
