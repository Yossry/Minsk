from . import models

from odoo import api, SUPERUSER_ID


def workaround_create_initial_rules(cr, registry):
    """Work around https://github.com/odoo/odoo/issues/4853."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    WH = env["stock.warehouse"]
    wh_ids = WH.sudo().search([("buy_vci_to_resupply", "=", True)])
    for wh in wh_ids:
        wh.write({"buy_vci_to_resupply": True})
