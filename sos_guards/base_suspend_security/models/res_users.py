from odoo import models

from ..base_suspend_security import BaseSuspendSecurityUid


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _browse(cls, ids, env, prefetch=None):
        """be sure we browse ints, ids laread is normalized"""
        return super(ResUsers, cls)._browse(
            [
                i if not isinstance(i, BaseSuspendSecurityUid)
                else super(BaseSuspendSecurityUid, i).__int__()
                for i in ids
            ], env, prefetch=prefetch)
