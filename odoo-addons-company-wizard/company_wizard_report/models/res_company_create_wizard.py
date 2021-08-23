# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResCompanyCreateWizard(models.TransientModel):
    _inherit = 'res.company.create.wizard'

    paperformat_id = fields.Many2one(
        string='Paper format', comodel_name='report.paperformat',
        default=lambda s: s._default_paperformat_id())

    def _default_paperformat_id(self):
        return self.env.ref('report.paperformat_euro')

    @api.multi
    def _prepare_company(self):
        self.ensure_one()
        res = super(ResCompanyCreateWizard, self)._prepare_company()
        res.update({
            'paperformat_id': self.paperformat_id.id,
        })
        return res
