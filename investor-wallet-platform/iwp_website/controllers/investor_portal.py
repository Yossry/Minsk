# Copyright 2018 Odoo SA <http://odoo.com>
# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import namedtuple
from itertools import groupby

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request
from odoo.tools.translate import _

from .user_form import InvestorCompanyForm, InvestorPersonForm
from .tools import monetary_to_text

# TODO: Try to not give sudo object to a view.


class InvestorPortal(CustomerPortal):

    @http.route(['/my/wallet/share'], type='http', auth="user", website=True)
    def my_wallet_share(self, **kw):
        """Wallet of share owned by the connected user."""
        values = self._prepare_portal_layout_values()
        shareline_mgr = request.env['share.line']
        user = request.env.user

        # Share lines owned by an investor
        sharelines = shareline_mgr.sudo().search(self.shareline_domain)

        data = []
        WalletLine = namedtuple(
            "WalletLine",
            [
                "structure",
                "total_amount",
                "display_buy_url",
                "buy_url",
                "sell_url",
                "lines",
            ]
        )
        sharelines = sharelines.sorted(key=lambda r: r.structure.name)
        grouped_sl = groupby(sharelines, lambda r: r.structure)
        for (structure, shares) in grouped_sl:
            lines = shareline_mgr  # New empty recordset
            buy_url = "/struct/%d/subscription" % (structure.id,)
            sell_url = "/struct/%d/sell" % (structure.id,)
            total_amount = 0
            for share in shares:
                total_amount += share.total_amount_line
                lines += share
            lines = lines.sorted(
                key=lambda r: r.sudo().effective_date,
                reverse=True,
            )
            data.append(
                WalletLine(
                    structure=structure,
                    total_amount=total_amount,
                    display_buy_url=self.display_share_action(user, structure),
                    buy_url=buy_url,
                    sell_url=sell_url,
                    lines=lines.sudo(),
                )
            )

        # Manual share suppression
        values["back_from_delete_share"] = False
        if "delete_share_success" in request.session:
            values["back_from_delete_share"] = True
            values["delete_share_success"] = request.session[
                "delete_share_success"
            ]
            del request.session["delete_share_success"]

        values.update({
            'data': data,
            'page_name': 'share_wallet',
            'default_url': '/my/wallet/share',
            'currency': (
                request.env['res.company']._company_default_get().currency_id
            ),
        })
        return request.render(
            'iwp_website.portal_my_wallet_share',
            values
        )

    @http.route('/my/history/share', type='http', auth="user", website=True)
    def my_history_share(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        register_mgr = request.env['subscription.register']
        sub_req_mgr = request.env['subscription.request']
        op_req_mgr = request.env['operation.request']

        searchbar_sortings = {
            'name': {'label': _('Structure Name'), 'order': ''},
            'date': {'label': _('Date'), 'order': 'date'},
        }

        # default sortby order
        # Order by name is done after the query
        if not sortby:
            sortby = 'date'
        sort_order = 'date desc'  # Always order by date

        registers = register_mgr.sudo().search(
            self.subscription_register_domain,
            order=sort_order,
        )
        subreqs = sub_req_mgr.sudo().search(
            self.subscription_request_domain,
            order='date desc',
        )
        opreqs = op_req_mgr.sudo().search(
            self.operation_request_domain,
            order='request_date desc',
        )

        if sortby == 'name':
            registers = registers.sorted(
                key=lambda r: r.structure.name if r.structure.name else ''
            )
            subreqs = subreqs.sorted(
                key=lambda r: r.structure.name if r.structure.name else ''
            )
            opreqs = opreqs.sorted(
                key=lambda r: r.structure.name if r.structure.name else ''
            )

        values.update({
            'registers': registers.sudo(),
            'subreqs': subreqs.sudo(),
            'opreqs': opreqs.sudo(),
            'page_name': 'share_history',
            'default_url': '/my/history/share',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'iwp_website.portal_my_history_share',
            values
        )

    @http.route(['/my/wallet/loan'], type='http', auth="user", website=True)
    def my_wallet_loan(self, sortby=None, **kw):
        """Wallet of loan owned by the connected user."""
        values = self._prepare_portal_layout_values()
        loanline_mgr = request.env['loan.issue.line']

        loan_domain = self.loan_issue_line_domain
        loan_domain += [("state", "=", "paid")]

        # Loan issue lines owned by an investor
        issuelines = loanline_mgr.sudo().search(loan_domain)

        data = []
        WalletLine = namedtuple(
            "WalletLine", ["structure", "total_amount", "lines"]
        )
        issuelines = issuelines.sorted(key=lambda r: r.structure.name)
        grouped_lil = groupby(issuelines, lambda r: r.structure)
        for (structure, loanlines) in grouped_lil:
            lines = loanline_mgr  # New empty recordset
            total_amount = 0
            for loanline in loanlines:
                total_amount += loanline.amount
                lines += loanline
            lines = lines.sorted(key=lambda r: r.sudo().date, reverse=True)
            data.append(WalletLine(
                structure=structure,
                total_amount=total_amount,
                lines=lines.sudo()
            ))

        # Manual loan suppression
        values["back_from_delete_loan"] = False
        if "delete_loan_success" in request.session:
            values["back_from_delete_loan"] = True
            values["delete_loan_success"] = request.session[
                "delete_loan_success"
            ]
            del request.session["delete_loan_success"]

        values.update({
            'data': data,
            'page_name': 'loan_wallet',
            'currency': (
                request.env['res.company']._company_default_get().currency_id
            ),
            'default_url': '/my/wallet/loan',
        })
        return request.render(
            'iwp_website.portal_my_wallet_loan',
            values
        )

    @http.route('/my/history/loan', type='http', auth="user", website=True)
    def my_history_loan(self, sortby=None, **kw):
        """Wallet of loan owned by the connected user."""
        values = self._prepare_portal_layout_values()
        loanline_mgr = request.env['loan.issue.line']

        # Order by
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'state': {'label': _('State'), 'order': 'state'},
            'struct': {'label': _('Structure Name'), 'order': 'date desc'},
        }
        if not sortby:
            sortby = 'struct'
        sort_order = searchbar_sortings[sortby]['order']

        # Loan issue lines owned by an investor
        issuelines = loanline_mgr.sudo().search(
            self.loan_issue_line_domain, order=sort_order,
        )

        if sortby == 'struct':
            issuelines = issuelines.sorted(key=lambda r: r.structure.name)

        values.update({
            'issuelines': issuelines,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'page_name': 'loan_history',
            'default_url': '/my/history/loan',
        })
        return request.render(
            'iwp_website.portal_my_history_loan',
            values
        )

    @http.route(
        [
            '/structure',
            '/structure/page/<int:page>',
        ],
        type='http', auth="user", website=True
    )
    def structures(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        struct_mgr = request.env['res.partner']
        user = request.env.user

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'type': {'label': _('Type'), 'order': 'structure_type'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        struct_count = struct_mgr.sudo().search_count(self.structure_domain)
        # make pager
        pager = portal_pager(
            url='/structure',
            url_args={
                'sortby': sortby
            },
            total=struct_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        structures = struct_mgr.sudo().search(
            self.structure_domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        data = []
        StructureLine = namedtuple(
            "StructureLine",
            [
                "structure",
                "display_share_action",
                "display_loan_action",
            ]
        )

        for struct in structures:
            data.append(
                StructureLine(
                    structure=struct.sudo(),
                    display_share_action=self.display_share_action(
                        user, struct
                    ),
                    display_loan_action=self.display_loan_action(
                        user, struct
                    )
                )
            )

        values.update({
            'data': data,
            'page_name': 'structures',
            'pager': pager,
            'default_url': '/structure',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'iwp_website.structures',
            values
        )

    @http.route()
    def account(self, redirect=None, **post):
        """Form processing to edit user details"""
        user = request.env.user
        is_company = user.parent_id.is_company
        if request.httprequest.method == "POST":
            form = self.user_form(
                data=request.params, context={"user": user}
            )
            if form.is_valid():
                if is_company:
                    self.process_company_form(form, context={"user": user})
                else:
                    self.process_user_form(form, context={"user": user})
                return request.redirect('/my/home')
        else:
            form = self.user_form(context={"user": user})
        qcontext = {"form": form, "page_name": "investor_details"}
        if is_company:
            return request.render(
                "iwp_website.investor_company_details", qcontext
            )
        return request.render("iwp_website.investor_details", qcontext)

    def user_form(self, data=None, context=None):
        """Return form object."""
        context = {} if context is None else context
        if context.get("user") and context["user"].parent_id.is_company:
            form = InvestorCompanyForm(
                initial=self.company_form_initial(context=context),
                data=data or None,
                context=context,
            )
            # Set the bank account readonly
            # No check should be performed on this field
            form.fields["bank_account"].readonly = True
            form.fields["bank_account"].required = False
            form.fields["bank_account"].validators = []
        else:
            form = InvestorPersonForm(
                initial=self.user_form_initial(context=context),
                data=data or None,
                context=context,
            )
            # Set the bank account readonly
            # No check should be performed on this field
            form.fields["bank_account"].readonly = True
            form.fields["bank_account"].required = False
            form.fields["bank_account"].validators = []
        return form

    def user_form_initial(self, context=None):
        """Initial data for user form."""
        context = {} if context is None else context
        user = context.get("user")
        initial = {}
        if user:
            initial.update(
                {
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "gender": str(user.gender),
                    "birthdate": (
                        user.birthdate_date.isoformat()
                        if user.birthdate_date
                        else ""
                    ),
                    "phone": user.phone,
                    "lang": user.lang,
                    "street": user.street,
                    "zip_code": user.zip,
                    "city": user.city,
                    "country": user.country_id.id if user.country_id else "",
                }
            )
            if user.bank_ids:
                initial["bank_account"] = user.bank_ids[0].acc_number
        return initial

    def company_form_initial(self, context=None):
        """Initial data for company user form."""
        initial = {}
        context = {} if context is None else context
        user = context.get("user")
        initial = {}
        if user:
            company = user.commercial_partner_id
            initial.update(
                {
                    "name": company.name,
                    "phone": company.phone,
                    "lang": company.lang,
                    "street": company.street,
                    "zip_code": company.zip,
                    "city": company.city,
                    "country": (
                        company.country_id and str(company.country_id.id)
                    ),
                    "rep_firstname": user.firstname,
                    "rep_lastname": user.lastname,
                    "rep_gender": str(user.gender),
                    "rep_birthdate": (
                        user.birthdate_date
                        and user.birthdate_date.isoformat()
                    ),
                    "rep_phone": user.phone,
                    "rep_lang": user.lang,
                    "rep_street": user.street,
                    "rep_zip_code": user.zip,
                    "rep_city": user.city,
                    "rep_country": user.country_id and str(user.country_id.id),
                }
            )
            if company.bank_ids:
                initial["bank_account"] = company.bank_ids[0].acc_number
        return initial

    def process_company_form(self, form, context=None):
        user = context.get("user")
        company = user.commercial_partner_id
        user.sudo().write(self.representative_vals(form, context))
        company.sudo().write(self.company_vals(form, context))

    def process_user_form(self, form, context=None):
        user = context.get("user")
        user.sudo().write(self.user_vals(form, context))

    def user_vals(self, form, context=None):
        """Return vals to add information on a res.users."""
        vals = {
            "firstname": form.cleaned_data["firstname"],
            "lastname": form.cleaned_data["lastname"],
            "gender": form.cleaned_data["gender"],
            "phone": form.cleaned_data["phone"],
            "birthdate_date": form.cleaned_data["birthdate"],
            "street": form.cleaned_data["street"],
            "city": form.cleaned_data["city"],
            "zip": form.cleaned_data["zip_code"],
            "country_id": form.cleaned_data["country"],
            "lang": form.cleaned_data["lang"],
        }
        return vals

    def company_vals(self, form, context=None):
        """Return vals to create company res.users."""
        vals = {
            "company_type": "company",
            "name": form.cleaned_data["name"],
            "lang": form.cleaned_data["lang"],
            "phone": form.cleaned_data["phone"],
            "street": form.cleaned_data["street"],
            "city": form.cleaned_data["city"],
            "zip": form.cleaned_data["zip_code"],
            "country_id": form.cleaned_data["country"],
        }
        return vals

    def representative_vals(self, form, context=None):
        """
        Return vals to create a representative for a company res.users.
        """
        vals = {
            "type": 'representative',
            "company_type": "person",
            "representative": True,
            "firstname": form.cleaned_data["rep_firstname"],
            "lastname": form.cleaned_data["rep_lastname"],
            "gender": form.cleaned_data["rep_gender"],
            "phone": form.cleaned_data["rep_phone"],
            "birthdate_date": form.cleaned_data["rep_birthdate"],
            "street": form.cleaned_data["rep_street"],
            "city": form.cleaned_data["rep_city"],
            "zip": form.cleaned_data["rep_zip_code"],
            "country_id": form.cleaned_data["rep_country"],
            "lang": form.cleaned_data["lang"],
        }
        return vals

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        # Shares
        shareline_mgr = request.env['share.line']
        share_amount = sum(
            r.total_amount_line
            for r in shareline_mgr.sudo().search(self.shareline_domain)
        )
        # Loans
        loanline_mgr = request.env['loan.issue.line']
        loan_domain = self.loan_issue_line_domain
        loan_domain += [("state", "!=", "cancelled"), ("state", "!=", "ended")]
        loanline_amount = sum(
            r.amount
            for r in (
                loanline_mgr.sudo()
                .search(self.loan_issue_line_domain)
                .filtered(
                    lambda r: (
                        r.state == "paid" or r.state == "waiting"
                        or r.state == "subscribed"
                    )
                )
            )
        )
        # Pending loan issue line
        pending_loan = loanline_mgr.sudo().search_count(
            self.loan_issue_line_domain
            + [
                ("state", "!=", "cancelled"),
                ("state", "!=", "ended"),
                ("state", "!=", "paid"),
            ]
        )
        # Pending subscription request
        subreq_mgr = request.env['subscription.request']
        opreq_mgr = request.env['operation.request']
        pending_share = 0
        pending_share += subreq_mgr.sudo().search_count(
            self.subscription_request_domain
            + [
                ("state", "!=", "cancelled"),
                ("state", "!=", "paid"),
                ("state", "!=", "transfer"),
            ]
        )
        pending_share += opreq_mgr.sudo().search_count(
            self.operation_request_domain
            + [
                ("state", "!=", "paid"),
                ("state", "!=", "cancelled"),
                ("state", "!=", "refused")
            ]
        )
        values.update({
            "invoice_count": 0,  # Hide invoice entry
            'share_amount': share_amount or 0,
            'loan_amount': loanline_amount or 0,
            'pending_share': "%d " % (pending_share,) + _("pending")
            if pending_share else None,
            'pending_loan': "%d " % (pending_loan,) + _("pending")
            if pending_loan else None,
            'monetary_to_text': monetary_to_text,
        })
        return values

    def display_share_action(self, user, structure):
        """Return True if the user can take share for the structure."""
        return bool([
            share for share in structure.share_type_ids
            if (
                share.state != "close"
                and share.display_on_website
                and (
                    (user.is_company and share.by_company)
                    or (not user.is_company and share.by_individual)
                )
            )
        ])

    def display_loan_action(self, user, structure):
        """Return True if the user can take loan for the structure."""
        return bool([
            loan for loan in structure.loan_issue_ids
            if (
                loan.state == "ongoing"
                and loan.display_on_website
                and (
                    (user.is_company and loan.by_company)
                    or (not user.is_company and loan.by_individual)
                )
            )
        ])

    @property
    def shareline_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def loan_issue_line_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def structure_domain(self):
        domain = [
            ('is_platform_structure', '=', True),
            ('state', '=', 'validated'),
            ('display_on_website', '=', True),
        ]
        return domain

    @property
    def subscription_register_domain(self):
        partner = request.env.user.partner_id
        domain = [
            '|',
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id_to', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def subscription_request_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '!=', 'paid'),
        ]
        return domain

    @property
    def operation_request_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('operation_type', '=', 'sell_back'),
            ('state', '!=', 'done'),
        ]
        return domain
