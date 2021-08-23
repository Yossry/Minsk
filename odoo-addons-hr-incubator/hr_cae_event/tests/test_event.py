# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime

from odoo import tests


class TestEvent(tests.common.TransactionCase):
    def test_compute_duration(self):
        event = self.browse_ref("event.event_0")
        event.date_begin = datetime(2020, 2, 1, 2, 0)
        event.date_end = datetime(2020, 2, 1, 4, 30)
        self.assertEquals(event.duration, 2.5)

        event.date_begin = datetime(2020, 2, 1, 2, 0)
        event.date_end = datetime(2020, 2, 10, 4, 30)
        self.assertEquals(event.duration, 218.5)
