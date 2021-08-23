# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase


class IWPBaseCase(EMCBaseCase):
    def as_iwp_user(self):
        self.uid = self.ref(
            "investor_wallet_platform_base.res_users_user_iwp_demo"
        )

    def as_iwp_manager(self):
        self.uid = self.ref(
            "investor_wallet_platform_base.res_users_manager_iwp_demo"
        )

# todo: test loan issue flow
