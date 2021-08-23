# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Date
from .test_iwp_base import IWPBaseCase
from odoo.exceptions import AccessError, ValidationError


class IWPIRulesCase(IWPBaseCase):
    def setUp(self):
        super(IWPIRulesCase, self).setUp()
        self.coopiteasy = self.browse_ref(
            "investor_wallet_platform_base"
            ".res_partner_structure_coopiteasy_demo"
        )
        self.coopcity = self.browse_ref(
            "investor_wallet_platform_base"
            ".res_partner_structure_coopcity_demo"
        )
        self.cie_share_product_template = self.browse_ref(
            "easy_my_coop.product_template_share_type_1_demo"
        )
        self.cc_share_product_template = self.browse_ref(
            "investor_wallet_platform_base"
            ".product_template_share_type_coopcity_1_demo"
        )
        self.cie_share_product_product = (
            self.env["product.product"]
            .search(
                [("product_tmpl_id", "=", self.cie_share_product_template.id)]
            )
            .id
        )
        self.cc_share_product_product = (
            self.env["product.product"]
            .search(
                [("product_tmpl_id", "=", self.cc_share_product_template.id)]
            )
            .id
        )
        self.request_values = {
            "structure": self.coopiteasy.id,
            "name": "test subscriber",
            "email": "test.login@test.coop",
            "address": "rue wagner 93",
            "zip_code": "4100",
            "city": "Seraing",
            "country_id": self.ref("base.be"),
            "share_product_id": self.cie_share_product_product,
            "lang": "en_US",
        }

    def test_emc_user_access_to_subscription_request(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        # own subscription request
        cie_request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        _ = cie_request.structure  # read
        cie_request.write({"name": "write passes"})
        vals = self.request_values.copy()
        vals["structure"] = self.coopiteasy.id
        self.env["subscription.request"].create(self.request_values)
        with self.assertRaises(AccessError):
            cie_request.unlink()

        # other structure's request
        coop_city_request = self.browse_ref(
            "investor_wallet_platform_base.subscription_request_2_demo"
        )
        with self.assertRaises(AccessError):
            _ = coop_city_request.structure  # read
        with self.assertRaises(AccessError):
            coop_city_request.write({"name": "write fails"})
        with self.assertRaises(AccessError):
            vals = self.request_values.copy()
            vals["structure"] = self.coopcity.id
            coop_city_request.create(vals)
        with self.assertRaises(AccessError):
            coop_city_request.unlink()

    def test_iwp_manager_access_to_all_subscription_request(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        request = self.env["subscription.request"].create(self.request_values)
        _ = request.structure
        request.write({"name": "write passes"})
        request.unlink()

    def test_emc_user_access_to_own_share_line(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        cooperator_id = self.ref("easy_my_coop.res_partner_cooperator_1_demo")
        vals = {
            "structure": self.coopiteasy.id,
            "share_product_id": self.cie_share_product_product,
            "share_number": 2,
            "share_unit_price": 50,
            "partner_id": cooperator_id,
            "effective_date": Date.today(),
        }

        # own share lines
        share_line = self.env["share.line"].create(vals)
        _ = share_line.structure
        share_line.write({"share_number": 10})
        with self.assertRaises(AccessError):
            share_line.unlink()

        # other share lines
        with self.assertRaises(AccessError):
            share_line = self.browse_ref(
                "investor_wallet_platform_base.share_line_coopcity_demo"
            )
            _ = share_line.structure
        with self.assertRaises(AccessError):
            share_line = self.browse_ref(
                "investor_wallet_platform_base.share_line_coopcity_demo"
            )
            share_line.write({"share_number": 10})
        with self.assertRaises(AccessError):
            vals["structure"] = self.coopcity.id
            self.env["share.line"].create(vals)
        with self.assertRaises(AccessError):
            share_line.unlink()

    def test_iwp_manager_access_to_all_share_line(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        cooperator_id = self.ref("easy_my_coop.res_partner_cooperator_1_demo")
        vals = {
            "structure": self.coopiteasy.id,
            "share_product_id": self.cie_share_product_product,
            "share_number": 2,
            "share_unit_price": 50,
            "partner_id": cooperator_id,
            "effective_date": Date.today(),
        }
        share_line = self.env["share.line"].create(vals)
        _ = share_line.structure
        share_line.write({"share_number": 666})
        with self.assertRaises(AccessError):
            share_line.unlink()

    def test_emc_user_access_to_own_operation_request(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        vals = {
            "operation_type": "transfer",
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_2_demo"
            ),
            "partner_id_to": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_1_demo"
            ).product_variant_id.id,
            "quantity": 1,
            "structure": self.coopiteasy.id,
        }
        operation_request = self.env["operation.request"].create(vals)
        _ = operation_request.structure
        operation_request.write({"quantity": 666})
        with self.assertRaises(AccessError):
            operation_request.unlink()

        vals = {
            "operation_type": "transfer",
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_2_demo"
            ),
            "partner_id_to": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_1_demo"
            ).product_variant_id.id,
            "quantity": 1,
            "structure": self.coopcity.id,
        }
        with self.assertRaises(AccessError):
            self.env["operation.request"].create(vals)

    def test_iwp_manager_access_to_all_operation_request(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        vals = {
            "operation_type": "transfer",
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_2_demo"
            ),
            "partner_id_to": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_1_demo"
            ).product_variant_id.id,
            "quantity": 1,
            "structure": self.coopiteasy.id,
        }
        operation_request = self.env["operation.request"].create(vals)
        _ = operation_request.structure
        operation_request.write({"quantity": 666})
        operation_request.unlink()

    def test_emc_user_access_to_own_subscription_register(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        vals = {
            "name": "create passes",
            "register_number_operation": 5,
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "date": Date.today(),
            "share_product_id": self.cie_share_product_product,
            "structure": self.coopiteasy.id,
        }
        register = self.env["subscription.register"].create(vals)
        _ = register.structure
        register.write({"name": "write passes"})
        with self.assertRaises(AccessError):
            register.unlink()

        vals = {
            "name": "create fails",
            "register_number_operation": 5,
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "date": Date.today(),
            "share_product_id": self.cc_share_product_product,
            "structure": self.coopcity.id,
        }
        with self.assertRaises(AccessError):
            self.env["subscription.register"].create(vals)

    def test_iwp_manager_access_to_all_subscription_register(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        vals = {
            "name": "create passes",
            "register_number_operation": 5,
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_1_demo"
            ),
            "date": Date.today(),
            "share_product_id": self.cie_share_product_product,
            "structure": self.coopiteasy.id,
        }
        register = self.env["subscription.register"].create(vals)
        _ = register.structure
        register.write({"register_number_operation": 2})
        with self.assertRaises(AccessError):
            register.unlink()

    def test_emc_user_access_to_own_loan_issue_and_lines(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        vals = {
            "name": "create passes",
            "face_value": 100,
            "taxes_rate": 0.03,
            "structure": self.coopiteasy.id,
        }
        with self.assertRaises(AccessError):
            self.env["loan.issue"].create(vals)

        loan_issue = self.env.ref("easy_my_coop_loan.loan_issue_1_demo")

        vals = {
            "loan_issue_id": loan_issue.id,
            "quantity": 3,
            "partner_id": self.ref(
                "easy_my_coop.res_partner_cooperator_3_demo"
            ),
            "date": Date.today(),
            "state": "subscribed",
            "structure": self.coopiteasy.id,
        }
        # fixme
        # loan = self.env["loan.issue.line"].create(vals)
        # _ = loan.structure
        # loan.write({"quantity": 3})
        # with self.assertRaises(AccessError):
        #     loan.unlink()

        vals = {
            "name": "create fails",
            "face_value": 100,
            "taxes_rate": 0.03,
            "structure": self.coopcity.id,
        }
        with self.assertRaises(AccessError):
            self.env["loan.issue"].create(vals)

        self.as_iwp_user()
        vals = {
            "name": "create fails",
            "face_value": 100,
            "taxes_rate": 0.03,
            "structure": self.coopcity.id,
        }
        loan_issue = self.env["loan.issue"].create(vals)

        self.as_emc_user()
        vals = {
            "loan_issue_id": loan_issue.id,
            "quantity": 3,
            "partner_id": self.ref(
                "easy_my_coop" ".res_partner_cooperator_3_demo"
            ),
            "date": Date.today(),
            "state": "subscribed",
            "structure": self.coopcity.id,
        }
        with self.assertRaises(AccessError):
            self.env["loan.issue.line"].create(vals)

    def test_iwp_manager_access_to_all_loan_issue_and_lines(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        vals = {
            "name": "create passes",
            "face_value": 100,
            "taxes_rate": 0.03,
            "structure": self.coopiteasy.id,
        }
        loan_issue = self.env["loan.issue"].create(vals)
        _ = loan_issue.structure
        loan_issue.write({"name": "write passes"})
        with self.assertRaises(AccessError):
            loan_issue.unlink()

        vals = {
            "loan_issue_id": loan_issue.id,
            "quantity": 3,
            "partner_id": self.ref(
                "easy_my_coop" ".res_partner_cooperator_3_demo"
            ),
            "date": Date.today(),
            "state": "subscribed",
            "structure": self.coopiteasy.id,
        }
        loan = self.env["loan.issue.line"].create(vals)
        _ = loan.structure
        loan.write({"quantity": 3})
        with self.assertRaises(AccessError):
            loan.unlink()

    def test_emc_user_access_to_own_invoices(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        vals = {"name": "create passes", "structure": self.coopiteasy.id}
        invoice = self.env["account.invoice"].create(vals)
        _ = invoice.structure
        invoice.write({"name": "write passes"})
        invoice.unlink()

        vals = {"name": "create fails", "structure": self.coopcity.id}
        # with self.assertRaises(AccessError):  # fixme
        # ?     def ensure_account_property(self, property_name):
        # or class TestAccountNoChartCommon(SavepointCase):
        #     self.env["account.invoice"].create(vals)

    def test_iwp_manager_access_to_all_invoices(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        vals = {"name": "create passes", "structure": self.coopiteasy.id}
        invoice = self.env["account.invoice"].create(vals)
        _ = invoice.structure
        invoice.write({"name": "write passes"})
        invoice.unlink()

    def test_emc_user_access_to_own_product_templates(self):
        self.as_emc_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = self.coopiteasy

        vals = {
            "name": "create passes",
            "is_share": True,
            "structure": self.coopiteasy.id,
        }
        with self.assertRaises(AccessError):
            self.env["product.template"].create(vals)

    def test_iwp_manager_access_to_all_product_templates(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id
        partner.structure = False

        vals = {
            "name": "create passes",
            "is_share": True,
            "structure": self.coopiteasy.id,
        }
        template = self.env["product.template"].create(vals)
        _ = template.structure
        template.write({"name": "write passes"})
        template.unlink()

        vals = {
            "name": "create passes",
            "is_share": False,
            "structure": self.coopiteasy.id,
        }
        template = self.env["product.template"].create(vals)
        _ = template.structure
        template.write({"name": "write passes"})
        template.unlink()

    def test_emc_user_access_to_own_partners(self):
        self.as_emc_user()
        vals = {
            "name": "own partner",
            "is_platform_structure": False,
        }
        own_partner = self.env['res.partner'].create(vals)
        self.env["coop.membership"].create({
            "partner_id": own_partner.id,
            "structure": self.coopiteasy.id,
            "member": True,
        })
        own_partner.write({"name": "write passes"})
        with self.assertRaises(AccessError):
            own_partner.unlink()

        # other partner
        self.env.user.structure = self.coopcity
        own_partner = self.env['res.partner'].browse(own_partner.id)
        # with self.assertRaises(AccessError):
        #     own_partner.write({"name": "write fails"}) # fixme
        with self.assertRaises(AccessError):
            own_partner.unlink()

    def test_emc_user_access_to_structures(self):
        self.as_emc_user()
        coopiteasy = self.env["res.partner"].browse(self.coopiteasy.id)
        _ = coopiteasy.name
        with self.assertRaises(AccessError):
            coopiteasy.write({"name": "write fails"})
        # with self.assertRaises(AccessError):
        #     self.env['res.partner'].create({
        #             "name": "create fails",
        #             "is_platform_structure": True,
        #         }) fixme
        with self.assertRaises(AccessError):
            coopiteasy.unlink()

        coopcity = self.env["res.partner"].browse(self.coopcity.id)
        with self.assertRaises(AccessError):
            _ = coopcity.name
        with self.assertRaises(AccessError):
            coopcity.write({"name": "write fails"})
        with self.assertRaises(AccessError):
            coopcity.unlink()

    def test_emc_manager_access_to_structures(self):
        self.as_emc_manager()
        coopiteasy = self.env["res.partner"].browse(self.coopiteasy.id)
        _ = coopiteasy.name
        coopiteasy.write({"name": "write passes"})
        # with self.assertRaises(AccessError):
        #     self.env["res.partner"].create(
        #         {"name": "create fails", "is_platform_structure": True} fixme
        #     )
        with self.assertRaises(AccessError):
            coopiteasy.unlink()

        coopcity = self.env["res.partner"].browse(self.coopcity.id)
        with self.assertRaises(AccessError):
            _ = coopcity.name
        with self.assertRaises(AccessError):
            coopcity.write({"name": "write fails"})
        with self.assertRaises(AccessError):
            coopcity.unlink()

    def test_iwp_user_access_to_partners(self):
        self.as_iwp_user()
        coopiteasy = self.env["res.partner"].browse(self.coopiteasy.id)
        _ = coopiteasy.name
        coopiteasy.write({"name": "write passes"})
        self.env["res.partner"].create(
            {"name": "create fails", "is_platform_structure": True}
        )
        with self.assertRaises(AccessError):
            coopiteasy.unlink()

        coopcity = self.env["res.partner"].browse(self.coopcity.id)
        _ = coopcity.name
        coopcity.write({"name": "write fails"})
        with self.assertRaises(AccessError):
            coopcity.unlink()

        own_partner = self.env['res.partner'].create({
            "name": "own partner",
            "is_platform_structure": False,
        })
        self.env["coop.membership"].create({
            "partner_id": own_partner.id,
            "structure": coopiteasy.id,
        })
        self.assertTrue(coopiteasy.id in own_partner.structure_ids.ids)
        own_partner.write({'name': 'write passes'})
        with self.assertRaises(AccessError):
            own_partner.unlink()

    def test_iwp_manager_access_to_partners(self):
        self.as_iwp_manager()
        coopiteasy = self.env["res.partner"].browse(self.coopiteasy.id)
        _ = coopiteasy.name
        coopiteasy.write({"name": "write passes"})
        self.env["res.partner"].create(
            {"name": "create fails", "is_platform_structure": True}
        )

        coopcity = self.env["res.partner"].browse(self.coopcity.id)
        _ = coopcity.name
        coopcity.write({"name": "write fails"})

        own_partner = self.env['res.partner'].create({
            "name": "own partner",
            "is_platform_structure": False,
        })
        self.env["coop.membership"].create({
            "partner_id": own_partner.id,
            "structure": coopiteasy.id,
        })
        self.assertTrue(coopiteasy.id in own_partner.structure_ids.ids)
        own_partner.write({'name': 'write passes'})

        own_partner.unlink()
        coopcity.unlink()
        coopiteasy.unlink()
