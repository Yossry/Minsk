import logging
import pprint
from urllib.parse import urljoin

import werkzeug

from odoo import SUPERUSER_ID, http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaystackController(http.Controller):
    _return_url = "/payment/paystack/return"

    @http.route(
        "/payment/paystack/return", type="http", auth="public", csrf=False, cors="*"
    )
    def paystack_return(self, **post):
        """ paystack contacts using GET, at least for accept """
        _logger.info(
            "paystack: entering form_feedback with post data %s", pprint.pformat(post)
        )  # debug
        # cr, uid, context = request.cr, SUPERUSER_ID, request.context
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")

        request.env["payment.transaction"].sudo().form_feedback(
            post, "paystack"
        )  # sale_order_id
        sale_order_id = int(request.session.get("sale_last_order_id"))
        transaction_id = (
            request.env["payment.transaction"]
            .sudo()
            .search([("sale_order_id", "=", sale_order_id)], limit=1)
        )
        params = {"transaction_id": transaction_id.id, "sale_order_id": sale_order_id}
        # shop_payment_validate = '/shop/payment/validate?{}'.format(
        #     urlencode(params))
        shop_payment_validate = "/shop/payment/validate"
        return werkzeug.utils.redirect(urljoin(base_url, shop_payment_validate))


class PaystackWebsiteSale(WebsiteSale):
    """."""

    @http.route("/shop/payment/validate", type="http", auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        order = request.website.sale_get_order()
        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            # confirm the trasaction.
            tx = request.env["payment.transaction"].browse(int(transaction_id))
            tx.sudo().write({"state": "done"})

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env["sale.order"].sudo().browse(int(sale_order_id))
            assert order.id == request.session.get("sale_last_order_id")
        if not order or (order.amount_total and not tx):
            return request.redirect("/shop")

        if (not order.amount_total and not tx) or tx.state in [
            "pending",
            "done",
            "authorized",
        ]:
            if not order.amount_total and not tx:
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(send_email=True).action_confirm()
        elif tx and tx.state == "cancel":
            # cancel the quotation
            order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == "draft":
            return request.redirect("/shop")

        return request.redirect("/shop/confirmation")
