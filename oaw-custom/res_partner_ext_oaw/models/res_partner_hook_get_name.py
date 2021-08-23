# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.base.models.res_partner import Partner


# Monkey Patching
# Overwrite the original _get_name
# i.e. https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/models/res_partner.py#L679-L703 # noqa
def _get_name(self):
    """ Utility method to allow name_get to be overrided without re-browse the
    partner """
    partner = self
    name = partner.name or ""
    if partner.ref:
        name = "[{}] {}".format(partner.ref, name)
    if partner.company_name or partner.parent_id:
        if not name and partner.type in ["invoice", "delivery", "other"]:
            name = dict(self.fields_get(["type"])["type"]["selection"])[partner.type]
        if not partner.is_company:
            name = "{}, {}".format(
                partner.commercial_company_name or partner.parent_id.name, name
            )
    if self._context.get("show_address_only"):
        name = partner._display_address(without_company=True)
    if self._context.get("show_address"):
        name = name + "\n" + partner._display_address(without_company=True)
    name = name.replace("\n\n", "\n")
    name = name.replace("\n\n", "\n")
    if self._context.get("address_inline"):
        name = name.replace("\n", ", ")
    if self._context.get("show_email") and partner.email:
        name = "{} <{}>".format(name, partner.email)
    if self._context.get("html_format"):
        name = name.replace("\n", "<br/>")
    if self._context.get("show_vat") and partner.vat:
        name = "{} ‒ {}".format(name, partner.vat)
    return name


class ResPartnerHookGetName(models.AbstractModel):
    _name = "res.partner.hook.get.name"
    _description = "Provide hook point for _get_name method"

    def _register_hook(self):
        Partner._get_name = _get_name
        return super(ResPartnerHookGetName, self)._register_hook()
