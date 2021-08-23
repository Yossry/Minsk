# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from .operation_request_form import OperationRequestForm

class WebsiteOperationRequest(http.Controller):

    @http.route(
        [
            '/struct/<int:struct_id>/sell',
            '/struct/<int:struct_id>/share/<int:finprod_id>/sell'
        ],
        type='http',
        auth='user',
        website=True,
    )
    def sell_finproduct(self, struct_id=None, finprod_id=None, **post):
        """Route for form to subscribe to a new share."""
        # Get structure and perform access check
        struct = request.env["res.partner"].sudo().browse(struct_id)
        if not struct or not struct.is_platform_structure:
            raise NotFound
        share_type = struct.share_type_ids.filtered(
            lambda r: r.id == finprod_id
        )
        form_context = {"struct": struct, "user": request.env.user}
        if share_type:
            form_context["share_type"] = share_type
        if request.httprequest.method == "POST":
            form = self.operation_request_form(
                data=request.params, context=form_context
            )
            if form.is_valid():
                self.process_operation_request_form(
                    form, context=form_context
                )
                return request.redirect(request.params.get("redirect", ""))
        else:
            form = self.operation_request_form(context=form_context)
        qcontext = {"form": form, "struct": struct}
        return request.render("iwp_website.sell_share", qcontext)

    def operation_request_form(self, data=None, context=None):
        """Return Form object."""
        form = OperationRequestForm(
            initial=self.operation_request_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def operation_request_form_initial(self, context=None):
        """Return initial for operation request form."""
        context = {} if context is None else context
        initial = {}
        user = context.get("user")
        struct = context.get("struct")
        share_type = context.get("share_type")
        if struct:
            if share_type:
                default_share_type = share_type
            else:
                share_types = request.env["product.template"].sudo()
                for shareline in user.commercial_partner_id.share_ids:
                    if shareline.share_product_id.structure == struct:
                        share_types |= (
                            shareline.share_product_id.product_tmpl_id
                        )
                default_share_type = (
                    share_types[0] if share_types else None
                )
            if default_share_type:
                initial["share_type"] = str(default_share_type.id)
                initial["quantity"] = 1
                initial["total_amount"] = (
                    default_share_type.list_price * initial["quantity"]
                )
        return initial

    def process_operation_request_form(self, form, context=None):
        """Process subscription share form."""
        vals = self.operation_request_vals(form, context=context)
        request.env['operation.request'].sudo().create(vals)

    def operation_request_vals(self, form, context=None):
        """Reutrn vals to create a new subscription request."""
        partner = context.get("user").commercial_partner_id
        struct = context.get("struct")
        share_type = request.env["product.template"].sudo().browse(
            int(form.cleaned_data["share_type"])
        )
        vals = {
            'partner_id': partner.id,
            'structure': struct.id,
            'state': 'draft',
            'operation_type': 'sell_back',
            "share_product_id": share_type.product_variant_id.id,
            'quantity': form.cleaned_data['quantity'],
        }
        return vals
