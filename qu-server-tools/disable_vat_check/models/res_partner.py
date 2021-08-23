# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright (c) 2018 QubiQ (http://www.qubiq.es)

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def check_vat(self):
        return True

    def check_vat_ch(self):
        return True

    def check_vat_ie(self):
        return True

    def check_vat_mx(self):
        return True

    def check_vat_no(self):
        return True

    def check_vat_pe(self):
        return True

    def check_vat_tr(self):
        return True

    def _construct_constraint_msg(self):
        return True

    def simple_vat_check(self):
        return True

    __check_vat_ch_re1 = []
    __check_vat_ch_re2 = []
