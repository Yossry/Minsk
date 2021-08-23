from .baseapi import BaseAPI


class Recipient(BaseAPI):
    def create(self, **kwargs):
        """
        Creates a new paystack customer account

        args:
        email -- Customer's email address
        first_name-- Customer's first name (Optional)
        last_name-- Customer's last name (Optional)
        phone -- optional 
        """
        url = self._url("/transferrecipient/")
        payload = {
            "type": "nuban",
            "name": kwargs.get("name"),
            "description": kwargs.get("description"),
            "account_number": kwargs.get("account_number"),
            "bank_code": kwargs.get("bank_code"),
            "currency": "NGN",
            "metadata": {"job": kwargs.get("metadata")},
        }
        return self._handle_request("POST", url, payload)

    def init_transfer(self, **kwargs):
        url = self._url("/transfer/")
        payload = {
            "source": kwargs.get("source"),
            "reason": kwargs.get("reason"),
            "amount": kwargs.get("amount"),
            "recipient": kwargs.get("recipient"),
        }
        return self._handle_request("POST", url, payload)

    def finalize_transfer(self, **kwargs):
        url = self._url("/transfer/finalize_transfer/")
        payload = {
            "otp": kwargs.get("otp"),
            "transfer_code": kwargs.get("transfer_code"),
        }
        return self._handle_request("POST", url, payload)
