from datetime import timedelta

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.afex_integration.models.res_partner \
    import AFEX_ADD_SYNC_DEFINITION

AFEX_BENEFICIARY_SYNC_EXPIRY = 120 # In seconds


class SyncAFEXBeneficiary(models.TransientModel):
    _name = 'sync.afex.beneficiary'
    _description = "AFEX Beneficiary Sync"

    name = fields.Text(string="AFEX Beneficiary Data", readonly=True)
    data_original = fields.Text(string="AFEX Beneficiary Data (Original)")
    bank_id = fields.Many2one('res.partner.bank', string="Bank")
    label_header = fields.Html(readonly=True)
    label_footer = fields.Html(readonly=True)
    date_retrieved = fields.Datetime()

    @api.model
    def default_get(self, default_fields):
        result = super(SyncAFEXBeneficiary, self).default_get(default_fields)

        if len(self.env.context.get('active_ids', [])) != 1:
            raise ValidationError(_("Please sync only one partner bank."))

        bank = self.env['res.partner.bank'].browse(
            self.env.context['active_id'])
        if not bank.afex_unique_id:
            raise ValidationError(_("No VendorID found for vendor name "
                                    "and currency. Try AFEX Sync first."))

        # Get/Find beneficiary
        url = 'beneficiary/find?VendorID=%s' % bank.afex_unique_id
        response_json = self.env['afex.connector'].afex_response(url)
        if response_json.get('ERROR', True):
            raise UserError(
                _("Error while getting/finding the beneficiary: %s") %
                  (response_json.get('message', ''))
            )

        # Get only the data existing in Odoo
        data = {}
        data_text = ""
        odoo_fields = list(AFEX_ADD_SYNC_DEFINITION.keys())
        odoo_fields += list(bank.return_afex_data().keys())
        odoo_fields.remove('TemplateType')
        odoo_fields.remove('HighLowValue')
        odoo_fields.append('VendorId')
        odoo_fields.append('BankRoutingCode')
        for field in response_json.keys():
            if field in odoo_fields:
                data[field] = response_json[field]
        for field in sorted(data.keys()):
            data_text += "%s: %s\n" % (field, data[field] or '')
        if 'BankRoutingCode' in data:
            data['BankRoutingcode'] = data['BankRoutingCode']

        label_header = ("<p>AFEX has this beneficiary information"
                        " for <b>%s</b> Vendor ID <b>%s</b></p>" %
                        (bank.partner_id.name, bank.afex_unique_id))
        label_footer = ("<p>Replace the beneficiary information you currently"
                        " hold in Odoo for <b>%s</b> with the information from"
                        " AFEX shown above?</p>" % (bank.partner_id.name))

        result.update({
            'name': data_text,
            'data_original': str(data),
            'bank_id': bank.id,
            'label_header': label_header,
            'label_footer': label_footer,
            'date_retrieved': fields.Datetime.now(),
        })
        return result

    @api.multi
    def action_sync(self):
        self.ensure_one()

        date_retrieved = fields.Datetime.from_string(self.date_retrieved) + \
            timedelta(seconds=AFEX_BENEFICIARY_SYNC_EXPIRY)
        now = fields.Datetime.from_string(fields.Datetime.now())
        if date_retrieved < now:
            view = self.env.ref(
                'afex_integration.sync_afex_beneficiary_timeout_view_form')
            return {
                'name': _("Odoo Server Error"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sync.afex.beneficiary',
                'res_id': self.id,
                'view_id': view.id,
                'target': 'new',
            }

        data = safe_eval(self.data_original)
        self.bank_id.sync_from_afex_beneficiary_find(data)
