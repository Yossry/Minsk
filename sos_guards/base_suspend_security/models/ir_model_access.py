
from odoo import models, api, tools
from ..base_suspend_security import BaseSuspendSecurityUid


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if isinstance(self.env.uid, BaseSuspendSecurityUid):
            return True
        return super(IrModelAccess, self).check(model, mode=mode, raise_exception=raise_exception)
