# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
import logging

from .loan_issue_form import LoanIssueLineForm

_logger = logging.getLogger(__name__)


class WebsiteLoanIssue(http.Controller):
    @http.route(
        [
            "/struct/<int:struct_id>/loan/subscription",
            "/struct/<int:struct_id>/loan/<int:loan_id>/subscription",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def subscribe_to_loan_issue(self, struct_id=None, loan_id=None, **post):
        """Route for form to subscribe to a new loan issue."""
        # Get structure and perform access check
        struct = request.env["res.partner"].sudo().browse(struct_id)
        if not struct or not struct.is_platform_structure:
            raise NotFound
        loan_issue = struct.loan_issue_ids.filtered(lambda r: r.id == loan_id)
        form_context = {"struct": struct, "user": request.env.user}
        if loan_issue:
            form_context["loan_issue"] = loan_issue
        if request.httprequest.method == "POST":
            form = self.loan_issue_line_form(
                data=request.params, context=form_context
            )
            if form.is_valid():
                self.process_loan_issue_line_form(form, context=form_context)
                return request.redirect(request.params.get("redirect", ""))
        else:
            form = self.loan_issue_line_form(context=form_context)
        qcontext = {"form": form, "struct": struct}
        return request.render("iwp_website.subscribe_to_loan_issue", qcontext)

    def loan_issue_line_form(self, data=None, context=None):
        """Return Form object."""
        form = LoanIssueLineForm(
            initial=self.loan_issue_line_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def loan_issue_line_form_initial(self, context=None):
        """Return initial for loan issue line form."""
        context = {} if context is None else context
        initial = {}
        user = context.get("user")
        struct = context.get("struct")
        loan_issue = context.get("loan_issue")
        if struct:
            if loan_issue:
                default_loan_issue = loan_issue
            else:
                default_loan_issues = (
                    request.env["loan.issue"]
                    .sudo()
                    .get_web_issues(user.commercial_partner_id.is_company)
                    .filtered(
                        lambda r: r.structure == struct and r.default_issue
                    )
                )
                default_loan_issue = (
                    default_loan_issues[0] if default_loan_issues else None
                )
            if default_loan_issue:
                initial["loan_issue"] = str(default_loan_issue.id)
                initial["quantity"] = max(
                    1,
                    round(
                        default_loan_issue.get_min_amount(
                            user.commercial_partner_id
                        )
                        / default_loan_issue.face_value
                    ),
                )
                initial["total_amount"] = (
                    default_loan_issue.face_value * initial["quantity"]
                )
        return initial

    def process_loan_issue_line_form(self, form, context=None):
        """Process loan issue line form."""
        vals = self.loan_issue_line_vals(form, context=context)
        request.env["loan.issue.line"].sudo().create(vals)

    def loan_issue_line_vals(self, form, context=None):
        """Reutrn vals to create a new loan issue line."""
        user = context.get("user")
        loan_issue = request.env["loan.issue"].browse(
            int(form.cleaned_data["loan_issue"])
        )
        vals = {
            "loan_issue_id": loan_issue.id,
            "partner_id": user.commercial_partner_id.id,
            "quantity": form.cleaned_data["quantity"],
        }
        return vals
