import hashlib
import logging
from datetime import datetime

# import urlparse
from urllib.parse import urljoin

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_paystack.controllers.main import PaystackController
from odoo.http import request

from .odoopaystack import Transaction

try:
    import simplejson as json
except ImportError:
    import json

your_secret_key = []

_logger = logging.getLogger(__name__)
tid = []
partner = []
currency = []


class PaymentAcquirerPaystack(models.Model):
    _inherit = "payment.acquirer"

    auth_url = ""

    provider = fields.Selection(selection_add=[("paystack", "Paystack")])
    terminal_id = fields.Char(string="Terminal ID")
    paystack_secret_key = fields.Char(
        string="Secret Key", required_if_provider="paystack", groups="base.group_user"
    )

    def _get_paystack_urls(self, environment):
        if environment == "prod":
            return {"paystack_standard_order_url": self.auth_url}
        else:
            return {"paystack_standard_order_url": self.auth_url}

    @api.multi
    def paystack_form_generate_values(self, values):
        # get key
        your_secret_key.append(self.paystack_secret_key)

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        paystack_tx_values = dict(values)

        TRANSACTION_ID = values["reference"]
        tid.append(TRANSACTION_ID)

        amount = values["amount"] * 100.00
        email = values["partner_email"]
        partner.append(values["partner_name"])
        currency.append(values["currency"].name)

        transaction = Transaction(authorization_key=your_secret_key[-1])
        response = transaction.initialize(
            email,
            amount,
            None,
            None,
            callback_url=base_url + "/payment/paystack/return",
        )
        self.auth_url = response[3]["authorization_url"]

        # response url where you get the response from payment gateway
        RESPONSE_URL = urljoin(base_url, PaystackController._return_url)

        to_encode_str = str(amount) + TRANSACTION_ID + RESPONSE_URL
        hashed_session = hashlib.md5(to_encode_str.encode("UTF-8")).hexdigest()

        ECHODATA = """<customerinfo><firstname>%s</firstname><lastname>%s</lastname><phoneno>%s</phoneno><email>%s
        </email><address>%s</address><city>%s</city><state>%s</state><zipcode>%s</zipcode><postalcode></postcode><country>%s
        </country><otherdetails></otherdetails></customerinfo>""" % (
            values["partner_first_name"],
            values["partner_last_name"],
            values["partner_phone"],
            values["partner_email"],
            values["partner_address"],
            values["partner_city"],
            values["partner_state"] and values["partner_state"].name or False,
            values["partner_zip"],
            values["partner_country"] and values["partner_country"].name or False,
        )

        paystack_tx_values.update(
            {
                "ECHODATA": ECHODATA,
                "CHECKSUM": hashed_session,
                "first_name": values["partner_first_name"],
                "last_name": values["partner_last_name"],
                "partner": values["partner"].id,
                "email": values["partner_email"],
                "zip": values["partner_zip"],
                "city": values["partner_city"],
                "country": values["partner_country"]
                and values["partner_country"].name
                or "",
                "state": values["partner_state"] and values["partner_state"].name or "",
                "DESCRIPTION": values["reference"],
                "LANGUAGE": values["partner_lang"],
                "CURRENCY_CODE": values["currency"].name,
                "CARD_TYPE": 0,
                "TRANSACTION_ID": values["reference"],
                "amount": values["amount"],
                "RESPONSE_URL": "%s"
                % urljoin(base_url, PaystackController._return_url),
            }
        )

        paystack_tx_values["custom"] = json.dumps(
            {"return_url": "%s" % paystack_tx_values.pop("return_url")}
        )

        return paystack_tx_values

    @api.multi
    def paystack_get_form_action_url(self):
        return self._get_paystack_urls(self.environment)["paystack_standard_order_url"]


class TxPaystack(models.Model):
    _inherit = "payment.transaction"

    _paystack_valid_tx_status = [0]

    paystack_txn_id = fields.Char(string="Transaction ID")
    debited_amount = fields.Char(string="Debited Amount")
    trans_num = fields.Char(string="Transaction Number")
    msg = fields.Text(string="Message from Paystack")
    debit_currency = fields.Char(string="Debit Currency")
    card_holder = fields.Char(string="Card Holder")
    card_no = fields.Char(string="Card Number")
    country_id = fields.Many2one("res.country", "Country")

    @api.model
    def _paystack_form_get_tx_from_data(self, data):
        if tid:
            reference = tid[-1]
        else:
            sale_order_id = request.session.get("sale_last_order_id")
            # if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            reference = order.name
            tid.append(reference)
        sale_order_id = request.session.get(
            "sale_last_order_id"
        ) or request.session.get("sale_order_id")
        reference = request.env["sale.order"].sudo().browse(sale_order_id)
        tx_ids = self.sudo().search(
            [
                "|",
                ("reference", "=", reference.name),
                ("paystack_txn_id", "=", reference.name),
                ("sale_order_id", "=", reference.id),
            ],
            limit=1,
        )
        if not tx_ids or len(tx_ids) > 1:
            error_msg = "Paystack: received data for reference %s" % (reference)
            if not tx_ids:
                error_msg += "; no order found"
            else:
                error_msg += "; multiple order found"
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids

    # validate the response from paystack. based on response validate the sale order
    def _paystack_form_validate(self, data):
        if your_secret_key:
            pass
        else:
            paystack = (
                self.env["payment.acquirer"]
                .sudo()
                .search([("provider", "=", "paystack")], limit=1)
            )
            if paystack:
                your_secret_key.append(paystack.paystack_secret_key)

        reference = data.get("reference")
        transaction = Transaction(authorization_key=your_secret_key[-1])
        response = transaction.verify(reference)[3]
        status = response.get("status")
        debit_currency = (
            self.env["res.users"].sudo().browse(1).company_id.currency_id.name or "NGN"
        )
        card_holder = request.env.user.partner_id.name

        if status == "success":
            sale_order_id = request.session.get("sale_last_order_id")
            # if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            reference = order.name
            tid.append(reference)
            self.write(
                {
                    "state": "done",
                    "date_validate": datetime.today(),
                    "paystack_txn_id": tid[-1],
                    "debited_amount": int(response.get("amount")) / 100.00,
                    "debit_currency": debit_currency,
                    "trans_num": response.get("customer").get("customer_code"),
                    "msg": response.get("gateway_response"),
                    "card_holder": card_holder,
                }
            )
            return True
        else:
            self.write(
                {
                    "state": "pending",
                    "date_validate": datetime.today(),
                    "trans_num": response.get("customer").get("customer_code"),
                    "msg": response.get("gateway_response"),
                    "card_holder": card_holder,
                    "debit_currency": debit_currency,
                }
            )
            return True

    def _paystack_s2s_get_invalid_parameters(self):
        """
         .. versionadded:: pre-v8 saas-3
         .. warning::

            Experimental code. You should not use it before OpenERP v8 official
            release.
        """
        invalid_parameters = []
        return invalid_parameters
