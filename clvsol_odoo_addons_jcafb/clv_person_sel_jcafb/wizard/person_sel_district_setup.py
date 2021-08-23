# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

# from odoo import api, fields, models
from odoo import api, models

_logger = logging.getLogger(__name__)


class PersonSelDistrictSetUp(models.TransientModel):
    _description = 'Person Sel District SetUp'
    _name = 'clv.person_sel.district.setup'

    # district_ids = fields.Many2many(
    #     comodel_name='clv.person_sel.district',
    #     relation='clv_person_sel_district_setup_rel',
    #     string='Person Selection Districts',
    #     domain=['|', ('active', '=', False), ('active', '=', True)],
    # )

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_person_sel_district_setup(self):
        self.ensure_one()

        PersonSelDistrict = self.env['clv.person_sel.district']

        cr = self.env.cr
        cr.execute('''
            SELECT
                res_partner.district AS district_name,
                address_category.id AS addr_category_id,
                COUNT(address.id) AS nr_address
            FROM
                clv_address AS address
            INNER JOIN
                res_partner AS res_partner
                    ON res_partner.id = address.partner_id
            LEFT JOIN
                clv_address_category_rel AS address_category_rel
                    ON address_category_rel.address_id = address.id
            LEFT JOIN
                clv_address_category AS address_category
                    ON address_category.id = address_category_rel.category_id
            WHERE
                address.state != 'unavailable'
            GROUP By
                district_name,
                addr_category_id
            ''')
        districts = cr.fetchall()

        for district in districts:

            _logger.info(u'%s %s %s (%s)', '>>>>>', district[0], district[1], district[2])

            if (district[0] is not None) and (district[0] != ''):

                name = district[0]

                person_sel_district = PersonSelDistrict.search([
                    ('name', '=', district[0]),
                ])

                if person_sel_district.id is False:

                    addr_category_ids = []
                    if district[1] is not None:
                        addr_category_ids.append((4, district[1]))

                    values = {
                        'name': name,
                        # 'code': code,
                        'addr_category_ids': addr_category_ids,
                        # 'nr_address': district[2],
                    }
                    PersonSelDistrict.create(values)

        return True

    # @api.multi
    # def do_delete_all(self):
    #     self.ensure_one()

    #     PersonSelDistrict = self.env['clv.person_sel.district']

    #     all_person_sel_districts = PersonSelDistrict.search([])
    #     all_person_sel_districts.unlink()

    #     return self._reopen_form()

    # @api.multi
    # def do_populate_all(self):
    #     self.ensure_one()

    #     PersonSelDistrict = self.env['clv.person_sel.district']
    #     person_sel_districts = PersonSelDistrict.search([])

    #     self.district_ids = person_sel_districts

    #     return self._reopen_form()
