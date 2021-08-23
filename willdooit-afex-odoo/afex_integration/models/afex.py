import json
import requests

from odoo import models, _
from odoo.exceptions import UserError


class AFEX(models.TransientModel):
    _name = 'afex.connector'
    _description = 'AFEX Connector Wizard'

    def afex_response(self, para_url,
                      payment=False, head=False, data=False, post=False):
        base_web = self.env['ir.config_parameter'].sudo().get_param('afex.url') \
            or "https://api.afex.com:7890/api/"
        if base_web[-1:] != '/':
            base_web += '/'
        url = "%s%s" % (base_web, para_url)
        key = payment and payment.journal_id.company_id.afex_api_key or \
            self.env.user.company_id.afex_api_key
        if not key:
            raise UserError(
                _('AFEX key not configured for this Company'))
        headers = {'API-key': key,
                   'Content-Type': 'application/json'
                   }
        if head:
            headers.update(head)
        if post:
            response = requests.post(
                url, headers=headers, data=json.dumps(data or {}))
        else:
            response = requests.get(url, headers=headers)
        ok = response.ok
        try:
            result = response.json()
        except:
            result = ''

        if ok and para_url == 'beneficiarycreate':
            ok = False
            if isinstance(result, list):
                ok = all(i.get('Code', 1) == 0 for i in result)
        if not ok:
            if isinstance(result, list):
                result = '\n\n' + \
                        '\n'.join(x.get('Name') or '' for x in result
                                  if x.get('Code') != 0)
            return {
                "ERROR": True,
                "code": response,
                "message": result,
                }

        if not isinstance(result, dict):
            result = {'items': result}
        result['ERROR'] = False
        return result
