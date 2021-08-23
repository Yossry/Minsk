
from odoo import api, models
from ..base_suspend_security import BaseSuspendSecurityUid


class Base(models.AbstractModel):

    _inherit = 'base'

    @api.model
    def suspend_security(self):
        return self.sudo(user=BaseSuspendSecurityUid(self.env.uid))
