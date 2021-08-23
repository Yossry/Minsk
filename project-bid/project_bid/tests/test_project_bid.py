from odoo.tests import common
from odoo import fields


class TestProjectBid(common.TransactionCase):
    def setUp(self):
        super(TestProjectBid, self).setUp()

        self.project_bid_temp_model = self.env["project.bid.template"]
        self.project_bid_model = self.env["project.bid"]
        self.project_bid_compo_model = self.env["project.bid.component"]
        self.uom_hour = self.env.ref("uom.product_uom_hour")
        self.product = self.env.ref("product.product_product_2")
        self.partenr = self.env.ref("base.partner_root")

        # Create Project Bid Template
        self.project_bid_temp = self.project_bid_temp_model.create(
            {
                "name": "Test Project Bid Template",
                "profit_rate": 1.0,
                "overhead_rate": 2.0,
                "labor_uom_id": self.uom_hour.id,
                "default_component_labor": [(6, 0, self.product.ids)],
            }
        )

        # Create Project Bid Parent
        self.project_bid_parent = self.project_bid_model.create(
            {
                "bid_template_id": self.project_bid_temp.id,
                "partner_id": self.partenr.id,
                "code": "Test PB",
                "name": "Test Project Bid",
                "created_by": self.partenr.id,
                "approved_by": self.partenr.id,
                "approved_on": fields.Date.today(),
                "due_by": fields.Date.today(),
                "notes": "Test Notes",
                "other_labor": [
                    (0, 0, {"product_id": self.product.id, "quantity": 1.0})
                ],
                "other_expenses": [
                    (0, 0, {"product_id": self.product.id, "quantity": 1.0})
                ],
                "overhead_rate": 2.0,
                "profit_rate": 3.0,
            }
        )

        # Create Project Bid
        self.project_bid = self.project_bid_model.create(
            {
                "bid_template_id": self.project_bid_temp.id,
                "partner_id": self.partenr.id,
                "parent_id": self.project_bid_parent.id,
                "code": "Test PB",
                "name": "Test Project Bid",
                "created_by": self.partenr.id,
                "approved_by": self.partenr.id,
                "approved_on": fields.Date.today(),
                "due_by": fields.Date.today(),
                "notes": "Test Notes",
                "other_labor": [
                    (0, 0, {"product_id": self.product.id, "quantity": 1.0})
                ],
                "other_expenses": [
                    (0, 0, {"product_id": self.product.id, "quantity": 1.0})
                ],
                "overhead_rate": 2.0,
                "profit_rate": 3.0,
            }
        )

        # Create Project Bid Component Parent
        self.project_bid_compo_1 = self.project_bid_compo_model.create(
            {
                "name": "Test Project Bid Component Parent",
                "overhead_rate": 1.0,
                "profit_rate": 2.0,
                "bid_id": self.project_bid.id,
                "bid_template_id": self.project_bid.bid_template_id.id,
                "labor": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Test Project Bid Component Labor",
                            "quantity": 1.0,
                        },
                    )
                ],
                "material_ids": [
                    (
                        0,
                        0,
                        {
                            "bid_id": self.project_bid.id,
                            "product_id": self.product.id,
                            "name": "Test Project Bid Component Labor",
                            "quantity": 10,
                            "default_code": "Test Project Bid Component "
                                            "Material",
                            "unit_cost": 100,
                        },
                    )
                ],
            }
        )

        # Create Project Bid Component Child
        self.project_bid_compo = self.project_bid_compo_model.create(
            {
                "name": "Test Project Bid Component Child",
                "bid_id": self.project_bid.id,
            }
        )

        # Onchang Project Bid Component
        data = {"bid_component_template_id": self.project_bid_compo_1.id}
        new_line = self.project_bid_compo_model.new(data)
        new_line.on_change_bid_component_template_id()

    def test_project(self):
        self.assertEqual(self.project_bid.state, "draft")
        self.project_bid.action_button_confirm()
        self.assertEqual(self.project_bid.state, "confirm")
        self.project_bid.action_button_approve()
        self.assertEqual(self.project_bid.state, "approve")
        self.assertEqual(
            self.project_bid.total_npm_percent,
            self.project_bid.wbs_total_npm_percent,
        )
        self.assertEqual(
            self.project_bid.total_gp, self.project_bid.wbs_total_gp
        )
        self.assertEqual(
            self.project_bid.total_overhead,
            self.project_bid.wbs_total_overhead,
        )
        self.assertEqual(
            self.project_bid.total_npm, self.project_bid.wbs_total_npm
        )
        self.assertEqual(
            self.project_bid.total_npm_percent,
            self.project_bid.wbs_total_npm_percent,
        )
