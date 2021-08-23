# Copyright 2020 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound
from datetime import date

from odoo import http
from odoo.http import request

from .manual_loan_form import ManualLoanForm


class ManualLoanAction(http.Controller):
    """Routes for editing manual loans on the website."""

    @http.route(
        "/struct/<int:struct_id>/loan/manual/new",
        type="http",
        auth="user",
        website=True,
    )
    def new_manual_loan(self, struct_id=None, **params):
        """Route for form to create a new manual loan"""
        struct = request.env["res.partner"].sudo().browse(struct_id)
        if not struct or not struct.is_platform_structure:
            raise NotFound
        form_context = {"struct": struct, "user": request.env.user}
        if request.httprequest.method == "POST":
            form = self.manual_loan_form(
                data=request.params, context=form_context
            )
            if form.is_valid():
                self.manual_loan_form_processing(form, context=form_context)
                return request.redirect(request.params.get("redirect", ""))
        else:
            form = self.manual_loan_form(context=form_context)
        qcontext = {"form": form, "struct": struct}
        return request.render("iwp_website.new_manual_loan_form", qcontext)

    @http.route(
        "/loan/<int:loan_line_id>/delete",
        type="http",
        auth="user",
        website=True,
    )
    def delete_manual_loan(self, loan_line_id=None, **params):
        """Route for form to delete a manual loan"""
        loanline = (
            request.env["loan.issue.line"].sudo().browse(loan_line_id).exists()
        )
        if not loanline or loanline.creation_mode != "manual":
            raise NotFound
        user = request.env.user
        request.session["delete_loan_success"] = False
        if loanline.partner_id == user.partner_id:
            loanline.unlink()
            request.session["delete_loan_success"] = True
        return request.redirect(params.get("nexturl"))

    def manual_loan_form(self, data=None, context=None):
        """Return form object"""
        form = ManualLoanForm(
            initial=self.manual_loan_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def manual_loan_form_initial(self, context=None):
        """Return initial for manual loan form."""
        context = {} if context is None else context
        initial = {}
        struct = context.get("struct")
        if struct:
            default_loan_issues = struct.loan_issue_ids.filtered(
                lambda r: r.display_on_website and r.default_issue
            )
            default_loan_issue = (
                default_loan_issues[0] if default_loan_issues else None
            )
            if default_loan_issue:
                initial["loan_issue"] = str(default_loan_issue.id)
        initial["quantity"] = 1
        initial["date"] = date.today().isoformat()
        return initial

    def manual_loan_form_processing(self, form, context=None):
        """Process manual loan form."""
        loan_line_mgr = request.env["loan.issue.line"]
        loan_line_mgr.sudo().create(
            self.loan_line_vals(form, context=context)
        )

    def loan_line_vals(self, form, context=None):
        """Return vals to create a loan issue line object"""
        context = {} if context is None else context
        user = context.get("user", request.env.user)
        vals = {
            "creation_mode": "manual",
            "state": "paid",
            "loan_issue_id": int(form.cleaned_data["loan_issue"]),
            "quantity": form.cleaned_data["quantity"],
            "date": form.cleaned_data["date"],
            "partner_id": user.partner_id.id,
        }
        return vals
