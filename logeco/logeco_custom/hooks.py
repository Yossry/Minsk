# Inspiration from OCA/project/project_task_code
from odoo import api, SUPERUSER_ID
import logging


_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    With this pre-init-hook we want to avoid an error when creating the UNIQUE
    ref constraint when the module is installed and before the post-init-hook
    is launched. We do this by filling all empty refs with a temporary unique value.
    Note that we do not check uniqueness of existing ref numbers.
    """
    _logger.info("Pre hook: setting empty partner ref with temporary value")

    env = api.Environment(cr, SUPERUSER_ID, dict())
    partner_obj = env["res.partner"]
    partners = partner_obj.search([])
    partners_no_ref = partner_obj.search([("ref", "=", False)])
    # _logger.info('Number of partners with existing reference = %s', len(partners_no_ref))
    # _logger.info('Number of partners with no reference yet = %s', len(partners_no_ref))
    for partner in partners_no_ref:
        partner.ref = "temp_" + str(partner.id)

    _logger.warning(
        "On sql constraint res_partner_unique_ref error, manually fill the ref for 'OdooBot', 'Public user', 'Default User Template' and 'Portal User Template' users, or check uniqueness of existing ref values, and update module."
    )


def post_init_hook(cr, registry):
    """
    This post-init-hook will update all temporary existing ref values using
    a sequence, starting from the highest existing number.
    """

    _logger.info(
        "Post hook: remplacing temporary partner ref with sequence numbers"
    )

    env = api.Environment(cr, SUPERUSER_ID, dict())
    partner_obj = env["res.partner"]
    partners = partner_obj.search([])
    partners_temp_ref = partner_obj.search(
        [("ref", "like", "temp_")], order="id"
    )
    sequence_obj = env["ir.sequence"]
    partner_sequence = sequence_obj.search(
        [("code", "=", "partner.reference")], limit=1
    )

    # _logger.info('Number of partners = %s', len(partners))
    # _logger.info('Number of partners with temp reference = %s', len(partners_temp_ref))

    refs_int = []
    for partner in partners:
        try:
            refs_int.append(int(partner.ref))
        except ValueError:
            pass
    if refs_int:
        max_ref = max(refs_int)
        # _logger.info('Max reference found = %s', max_ref)
        partner_sequence.write({"number_next": max_ref + 1})

    for partner in partners_temp_ref:
        next_ref = sequence_obj.next_by_code("partner.reference")
        partner.ref = next_ref
