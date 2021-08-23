# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound
from datetime import date

from odoo import http
from odoo.http import request

from .manual_share_form import ManualShareForm


class ManualShareAction(http.Controller):
    """Routes for editing manual shares on the website."""

    @http.route(
        "/struct/<int:struct_id>/share/manual/new",
        type="http",
        auth="user",
        website=True,
    )
    def new_manual_share(self, struct_id=None, **params):
        """Route for form to create a new manual share"""
        struct = request.env["res.partner"].sudo().browse(struct_id)
        if not struct or not struct.is_platform_structure:
            raise NotFound
        form_context = {"struct": struct, "user": request.env.user}
        if request.httprequest.method == "POST":
            form = self.manual_share_form(
                data=request.params, context=form_context
            )
            if form.is_valid():
                self.manual_share_form_processing(form, context=form_context)
                return request.redirect(request.params.get("redirect", ""))
        else:
            form = self.manual_share_form(context=form_context)
        qcontext = {"form": form, "struct": struct}
        return request.render("iwp_website.new_manual_share_form", qcontext)

    @http.route(
        "/share/<int:share_line_id>/delete",
        type="http",
        auth="user",
        website=True,
    )
    def delete_manual_share(self, share_line_id=None, **params):
        """Route for form to delete a manual share"""
        shareline = (
            request.env["share.line"].sudo().browse(share_line_id).exists()
        )
        if not shareline or shareline.creation_mode != "manual":
            raise NotFound
        user = request.env.user
        request.session["delete_share_success"] = False
        if shareline.partner_id == user.partner_id:
            shareline.unlink()
            request.session["delete_share_success"] = True
        return request.redirect(params.get("nexturl"))

    def manual_share_form(self, data=None, context=None):
        """Return form object"""
        form = ManualShareForm(
            initial=self.manual_share_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def manual_share_form_initial(self, context=None):
        """Return initial for manual share form."""
        context = {} if context is None else context
        initial = {}
        struct = context.get("struct")
        if struct:
            default_share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.default_share_product
            )
            default_share_type = (
                default_share_types[0] if default_share_types else None
            )
            if default_share_type:
                initial["share_type"] = str(default_share_type.id)
        initial["quantity"] = 1
        initial["date"] = date.today().isoformat()
        return initial

    def manual_share_form_processing(self, form, context=None):
        """Process manual share form."""
        share_line_mgr = request.env["share.line"]
        share_line_mgr.sudo().create(
            self.share_line_vals(form, context=context)
        )

    def share_line_vals(self, form, context=None):
        """Return vals to create a share line object"""
        context = {} if context is None else context
        user = context.get("user", request.env.user)
        share_type = (
            request.env["product.template"]
            .sudo()
            .browse(int(form.cleaned_data["share_type"]))
        )
        vals = {
            "creation_mode": "manual",
            "structure": context["struct"].id,
            "share_product_id": share_type.product_variant_id.id,
            "share_number": form.cleaned_data["quantity"],
            "share_unit_price": share_type.list_price,
            "effective_date": form.cleaned_data["date"],
            "partner_id": user.partner_id.id,
        }
        return vals
