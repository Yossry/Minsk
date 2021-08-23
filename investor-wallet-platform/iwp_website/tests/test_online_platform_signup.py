# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .test_iwp_base import TestIWPBase


class TestIWPSignup(TestIWPBase):
    def test_signup_investor_success(self):
        res = self.http_get("/web/investor/signup")
        self.assertEquals(res.status_code, 200)

        data = {
            "login": "robin@desbois.coop",
            "confirm_login": "robin@desbois.coop",
            "password": "test",
            "confirm_password": "test",
            "firstname": "Robin",
            "lastname": "Desbois",
            "gender": "other",
            "birthdate_date": "1990-09-21",
            "phone": "0472947202",
            "iban": "FR7642559000011234567890121",
            "lang": "en_US",
            "street": "rue Fontaine d'Amour",
            "zip_code": "1030",
            "city": "Bruxelles",
            "country_id": "20",
            "token": "",
            "redirect": "",
            "csrf_token": self.get_csrf_token(res),
        }
        res = self.http_post("/web/investor/signup", data)
        self.assertEquals(res.status_code, 200)

    def test_signup_investor_fail_different_confirm_login(self):
        res = self.http_get("/web/investor/signup")
        data = {
            "login": "robin@desbois.coop",
            "confirm_login": "robin@desforets.coop",
            "password": "test",
            "confirm_password": "test",
            "firstname": "Robin",
            "lastname": "Desbois",
            "gender": "other",
            "birthdate_date": "1990-09-21",
            "phone": "0472947202",
            "iban": "FR7642559000011234567890121",
            "lang": "en_US",
            "street": "rue Fontaine d'Amour",
            "zip_code": "1030",
            "city": "Bruxelles",
            "country_id": "20",
            "token": "",
            "redirect": "",
            "csrf_token": self.get_csrf_token(res),
        }
        res = self.http_post("/web/investor/signup", data)
        self.assertEquals(res.status_code, 200)

        doc = self.html_doc(res)
        alert_danger = doc.xpath("//p[contains(@class, 'alert-danger')]")
        self.assertTrue(len(alert_danger) > 0)

    def test_signup_investor_fail_different_confirm_password(self):
        res = self.http_get("/web/investor/signup")
        data = {
            "login": "robin@desbois.coop",
            "confirm_login": "robin@desbois.coop",
            "password": "test",
            "confirm_password": "prod",
            "firstname": "Robin",
            "lastname": "Desbois",
            "gender": "other",
            "birthdate_date": "1990-09-21",
            "phone": "0472947202",
            "iban": "FR7642559000011234567890121",
            "lang": "en_US",
            "street": "rue Fontaine d'Amour",
            "zip_code": "1030",
            "city": "Bruxelles",
            "country_id": "20",
            "token": "",
            "redirect": "",
            "csrf_token": self.get_csrf_token(res),
        }
        res = self.http_post("/web/investor/signup", data)
        self.assertEquals(res.status_code, 200)

        doc = self.html_doc(res)
        alert_danger = doc.xpath("//p[contains(@class, 'alert-danger')]")
        self.assertTrue(len(alert_danger) > 0)

    def test_signup_company_investor_success(self):
        res = self.http_get("/web/investor/company/signup")
        data = {
            "login": "robin@desbois.coop",
            "confirm_login": "robin@desbois.coop",
            "password": "test",
            "confirm_password": "test",
            "name": "ERU",
            "phone": "0472947202",
            "iban": "FR7642559000011234567890121",
            "lang": "en_US",
            "street": "rue Fontaine d'Amour",
            "zip_code": "1030",
            "city": "Bruxelles",
            "country_id": "20",
            "rep_firstname": "Robin",
            "rep_lastname": "Desbois",
            "gender": "other",
            "rep_birthdate_date": "1990-09-21",
            "rep_phone": "0472947202",
            "rep_street": "rue Fontaine d'Amour",
            "rep_zip_code": "1030",
            "rep_city": "Bruxelles",
            "rep_country_id": "20",
            "token": "",
            "redirect": "",
            "csrf_token": self.get_csrf_token(res),
        }
        res = self.http_post("/web/investor/company/signup", data)
        self.assertEquals(res.status_code, 200)
