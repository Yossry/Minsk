# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    access_token = fields.Char('Access Token', groups="base.group_user,odoo_marketplace.marketplace_draft_seller_group")

    @api.multi
    def unlink(self):
        ctx = self._context
        if ctx.get('mp_img_attachment'):
            user = self.env.user
            seller_grp = 'odoo_marketplace.marketplace_seller_group'
            officer_grp = 'odoo_marketplace.marketplace_officer_group'
            if user.partner_id.seller and user.has_group(seller_grp) and not user.has_group(officer_grp):
                return super(IrAttachment, self).sudo().unlink()
        return super(IrAttachment, self).unlink()
