# Copyright 2014-2015 Camptocamp SA - Yannick Vaucher, Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPropagateOwner(TransactionCase):
    def test_it_propagates_empty_owner_to_the_move(self):
        self.so.action_button_confirm()

        self.assertEqual(1, len(self.so.picking_ids))
        self.assertFalse(self.so.picking_ids.move_lines[0].restrict_partner_id)

    def test_it_propagates_owner_to_the_move(self):
        self.sol.stock_owner_id = self.partner.id

        self.so.action_button_confirm()

        self.assertEqual(1, len(self.so.picking_ids))
        self.assertEqual(
            self.so.picking_ids.move_lines[0].restrict_partner_id, self.partner
        )

    def setUp(self):
        super(TestPropagateOwner, self).setUp()
        self.SO = self.env["sale.order"]
        self.SOL = self.env["sale.order.line"]

        # this product has some stock in demo data
        product = self.env.ref("product.product_product_6")
        self.partner = self.env.ref("base.res_partner_2")

        self.so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )
        self.sol = self.env["sale.order.line"].create(
            {"name": "/", "order_id": self.so.id, "product_id": product.id}
        )
