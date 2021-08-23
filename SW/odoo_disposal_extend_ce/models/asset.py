# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset.custom'
    
    disposal_number = fields.Char(
        string='Disposal Number',
        readonly=True,
    )
    reason_disposal = fields.Char(
        string='Reason for Disposal',
    )

    @api.model
    def create(self, vals):
        if vals.get("use_disposal", False):
            number = self.env['ir.sequence'].next_by_code('disposal.specification.seq')
            vals.update({
                'disposal_number': number
                })
        return super(AccountAsset, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get("use_disposal") and not rec.disposal_number:
                number = self.env['ir.sequence'].next_by_code('disposal.specification.seq')
                vals.update({
                    'disposal_number': number
                    })
        return super(AccountAsset, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
