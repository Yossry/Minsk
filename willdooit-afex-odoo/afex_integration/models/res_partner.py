from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


AFEX_ADD_SYNC_DEFINITION = {
    'RemittanceLine1': {
        'name': 'Remittance Line 1',
        'length': 35,
        },
    'RemittanceLine3': {
        'name': 'Remittance Line 3',
        'length': 35,
        },
    'RemittanceLine4': {
        'name': 'Remittance Line 4',
        'length': 35,
        },
    'BankSWIFTBIC': {
        'name': 'Bank SWIFT BIC',
        },
    'BankRoutingcode': {
        'name': 'Bank Routing Code',
        },
    'IntermediaryBankSWIFTBIC': {
        'name': 'Intermediary Bank SWIFT BIC',
        },
    'IntermediaryBankName': {
        'name': 'Intermediary Bank Name',
        },
    'IntermediaryBankRoutingCode': {
        'name': 'Intermediary Bank Routing Code',
        },
    'IntermediaryBankAccountNumber': {
        'name': 'Intermediary Bank Account Number',
        },
    }
AFEX_ADD_SYNC_FIELDS = [
    (k, v['name']) for k, v in AFEX_ADD_SYNC_DEFINITION.items()
    ]
AFEX_BENE_CODES = {
    100013: 'RemittanceLine1',
    100018: 'BankAddress1',
    100019: 'BankAddress2',
    100020: 'BankAddress3',
    100022: 'BankName',
    100030: 'IntermediaryBankCountryCode',
    100031: 'IntermediaryBankName',
    100033: 'IntermediaryBankSWIFTBIC',
    }


# This message is included when an error occurs, and is intended to help users
# determine odoo fields vs AFEX fields

PARTNER_AFEX_DESC_TEXT = """

NOTES:

    A new Partner will be linked to an existing AFEX Beneficiary if the Beneficiary has already been setup in AFEX with the exact same name.

When creating a new Beneficiary:

    Currency comes from the selected bank's currency.
    The Beneficiary name is the name of this Partner.
    All payments to the beneficiary will be via wire.
    The Notification Email will be the bank's Payment Notification Email Address.
    Beneficiary Address Details come from this Partner (address line 2 is optional).
    The Bank Name is the name of the Partner's Bank Account.
    Bank Account Number is the Partner's Bank Account Number.
    Remittance Lines and Other Important Additional Information will come from the Partner's Bank "AFEX Sync Information".
    (If remittance line 1 is not entered, your company name will be sent).
"""


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    is_afex = fields.Boolean(
        string="AFEX Beneficiary", default=False,
        copy=False)
    afex_bank_country_id = fields.Many2one(
        'res.country',
        string="AFEX Bank Country",
        copy=False)
    afex_int_bank_country_id = fields.Many2one(
        'res.country',
        string="AFEX Intermediary Bank Country",
        copy=False)
    afex_corporate = fields.Boolean(
        string="AFEX Corporate", default=False,
        help='This must be checked if the beneficiary is a Corporation and '
        'left blank if the beneficiary is an Individual',
        copy=False)
    add_afex_info_ids = fields.One2many(
        'afex.additional.sync.fields', 'bank_id',
        string="AFEX Sync Information",
        copy=False)
    afex_unique_id = fields.Char(
        string="VendorID",
        copy=False
    )
    afex_sync_status = fields.Selection(
        [('needed', 'Sync Needed'),
         ('done', 'Synchronised'),
         ],
        string='AFEX Status',
        default='needed',
        readonly=True
        )
    afex_purpose_of_payment_id = fields.Many2one(
        'afex.purpose.of.payment',
        string="Remittance Line 2",
        copy=False)
    partner_country_id = fields.Many2one(
        related='partner_id.country_id',
        readonly=True,
        store=True)
    afex_payment_notify_email = fields.Char(
        string="Payment Notification Email Address",
        copy=False
    )

    @api.onchange('is_afex', 'afex_bank_country_id', 'currency_id',
                  'partner_id')
    def onchange_purpose_of_payment(self):
        self.afex_purpose_of_payment_id = False
        if (self.is_afex and self.afex_bank_country_id and self.currency_id
                and self.partner_country_id):
            # Get purpose of payments
            url = ('purposeOfPayment?BankCountryCode=%s&Currency=%s'
                   '&BeneficiaryCountryCode=%s&HighValue=TRUE'
                   % (self.afex_bank_country_id.code, self.currency_id.name,
                      self.partner_country_id.code)
                   )
            response_json = self.env['afex.connector'].afex_response(
                url)
            if response_json.get('ERROR', True):
                raise UserError(
                    _("Error while getting purpose of payment: %s") %
                      (response_json.get('message', ''))
                )

            # Create/activate purpose of payments retrieved
            Purpose = self.env['afex.purpose.of.payment']
            purposes = Purpose.search([
                ('afex_bank_country_id', '=', self.afex_bank_country_id.id),
                ('currency_id', '=', self.currency_id.id),
                ('partner_country_id', '=', self.partner_country_id.id),
                ('active', 'in', [False, True]),
                ])
            purposes_retrieved = Purpose
            for result in response_json.get('items', []):
                # Checked if purpose of payment code is already existing for
                #   bank country, partner country and currency. If not create
                #   new purpose of payment.
                purpose = purposes.filtered(lambda p: p.code==result['Code'])
                if not purpose:
                    purpose = Purpose.create(
                        {'name': result['Description'],
                         'code': result['Code'],
                         'afex_bank_country_id': self.afex_bank_country_id.id,
                         'currency_id': self.currency_id.id,
                         'partner_country_id': self.partner_country_id.id,
                         })
                elif purpose and not purpose.active:
                    purpose.write({'active': True})
                purposes_retrieved |= purpose

            # Deactivate purpose of payments that are not retrieved
            (purposes - purposes_retrieved).write({'active': False})

    @api.multi
    def write(self, vals):
        for bank in self:
            if 'currency_id' in vals and bank.afex_unique_id:
                raise UserError(
                    _('Cannot change Bank Currency for a Bank which is'
                      ' already synchronised with AFEX'))
        if 'afex_sync_status' not in vals:
            vals['afex_sync_status'] = 'needed'
        return super(ResPartnerBank, self).write(vals)

    def sync_beneficiary_afex(self):
        for bank in self:
            if not bank.currency_id:
                raise UserError(
                        _('AFEX Beneficiary Bank Account does not contain '
                          'a Currency'))

            # if no afex id, first see if there is one
            if not bank.afex_unique_id:
                bank.update_beneficiary_afex_id()

            # if bank has afex id or just linked, then send details
            if bank.afex_unique_id:
                bank.update_beneficiary_afex()
            else:
                new_afex_id = '%s%s%s' % \
                    (bank.partner_id.id, bank.currency_id.name or 'x', bank.id)

                url = "beneficiarycreate"
                data = bank.return_afex_data()
                data['VendorId'] = new_afex_id
                # create new beneficiary
                response_json = self.env['afex.connector'].afex_response(
                        url, data=data, post=True)
                if response_json.get('ERROR', True):
                    raise UserError(
                        _('Error while creating beneficiary: %s %s') %
                        (response_json.get('message', ''),
                         _(PARTNER_AFEX_DESC_TEXT))
                    )
                bank.sync_from_afex_beneficiary(response_json)

                bank.afex_unique_id = new_afex_id
            bank.afex_sync_status = 'done'

    def update_beneficiary_afex_id(self):
        self.ensure_one()
        # update the bank afex ID with get from afex
        url = "beneficiary"
        response_json = self.env['afex.connector'].afex_response(url)
        if response_json.get('ERROR', True):
            raise UserError(
                    _('Error while checking existing beneficiaries: %s') %
                    (response_json.get('message', ''),)
                    )
        for item in response_json.get('items', []):
            if item.get('Name', '') == self.partner_id.name \
                    and item.get('Currency', '') == self.currency_id.name:
                if not item.get('VendorId'):
                    raise UserError(
                        _('Vendor name and currency exists on AFEX but'
                          " it doesn't have a Vendor Id")
                        )
                if self.search(
                        [('afex_unique_id', '=', item['VendorId'])]):
                    raise UserError(
                        _('Vendor name and currency exists on AFEX but'
                          ' already linked on Odoo to another beneficiary')
                        )
                self.afex_unique_id = item['VendorId']
                break

    def update_beneficiary_afex(self):
        self.ensure_one()
        # update afex with new details
        url = "beneficiaryupdate"
        data = self.return_afex_data()
        data['VendorId'] = self.afex_unique_id
        response_json = self.env['afex.connector'].afex_response(
                url, data=data, post=True)
        if response_json.get('ERROR', True):
            raise UserError(
                _('Error while updating beneficiary: %s%s') %
                (response_json.get('message', ''),
                 _(PARTNER_AFEX_DESC_TEXT))
                )
        self.sync_from_afex_beneficiary(response_json)

    @api.multi
    def sync_from_afex_beneficiary(self, response_json):
        self.ensure_one()
        bank_data = {}

        # Update RemittanceLine1, Intermediary Bank and Bank details
        #   from AFEX api response
        for item in response_json.get('items', []):
            code = item.get('InformationCode', False)
            if not code:
                continue

            message = item.get('InformationMessage', '')
            new_data = message[message.index(' to ')+5 : -1] or False
            if AFEX_BENE_CODES.get(code) == 'BankName':
                bank_data['name'] = new_data
            elif AFEX_BENE_CODES.get(code) == 'BankAddress1':
                bank_data['street'] = new_data
            elif AFEX_BENE_CODES.get(code) == 'BankAddress2':
                bank_data['street2'] = new_data
            elif AFEX_BENE_CODES.get(code) == 'BankAddress3':
                bank_data['city'] = new_data
            elif AFEX_BENE_CODES.get(code) in ['RemittanceLine1',
                                               'IntermediaryBankName',
                                               'IntermediaryBankSWIFTBIC']:
                self.update_afex_additional_sync_fields(
                    AFEX_BENE_CODES.get(code), new_data)
            elif AFEX_BENE_CODES.get(code) == 'IntermediaryBankCountryCode':
                country = self.env['res.country'].search(
                    [('code', '=', new_data)], limit=1)
                if country:
                    self.afex_int_bank_country_id = country.id

        # Update partner bank's bank
        if 'name' not in bank_data and self.bank_id:
            bank_data['name'] = self.bank_id.name
        if bank_data.get('name'):
            Bank = self.env['res.bank']
            bank = Bank.search([('name', '=', bank_data['name'])], limit=1)
            if not bank:
                # Create bank data if not existing
                bank = Bank.create(bank_data)
            self.bank_id = bank.id
        else:
            self.bank_id = False

    @api.multi
    def sync_from_afex_beneficiary_find(self, response_json):
        self.ensure_one()
        partner_bank_data = {
            'afex_corporate': response_json.get('Corporate', False),
            'afex_payment_notify_email':
                response_json.get('NotificationEmail', False),
        }

        # Update Bank
        bank_data = {
            'name': response_json.get('BankName', False),
            'street': response_json.get('BankAddress1', False),
            'street2': response_json.get('BankAddress2', False),
            'city': response_json.get('BankAddress3', False),
        }
        if 'name' not in bank_data and self.bank_id:
            bank_data['name'] = self.bank_id.name
        if bank_data.get('name'):
            Bank = self.env['res.bank']
            bank = Bank.search([('name', '=', bank_data['name'])], limit=1)
            if not bank:
                # Create bank data if not existing
                bank = Bank.create(bank_data)
            else:
                bank.write(bank_data)
            partner_bank_data['bank_id'] = bank.id
        else:
            partner_bank_data['bank_id'] = False

        # Update Partner
        partner_data = {
            'street': response_json.get('BeneficiaryAddressLine1', False),
            'street2': response_json.get('BeneficiaryAddressLine2', False),
            'city': response_json.get('BeneficiaryCity', False),
            'zip': response_json.get('BeneficiaryPostalCode', False),
        }
        if response_json.get('BeneficiaryName'):
            partner_data['name'] = response_json['BeneficiaryName']
        state_code = response_json.get('BeneficiaryRegionCode', False)
        country_code = response_json.get('BeneficiaryCountryCode', False)
        country = self.env['res.country'].search(
            [('code', '=', country_code)], limit=1)
        partner_data['country_id'] = country.id
        state = self.env['res.country.state'].search(
            [('code', '=', state_code), ('country_id', '=', country.id)],
            limit=1,
            )
        partner_data['state_id'] = state.id
        self.partner_id.with_context(sync_done=True).write(partner_data)

        # Update AFEX Additional Sync Fields
        for field in AFEX_ADD_SYNC_DEFINITION.keys():
            self.update_afex_additional_sync_fields(
                field, response_json.get(field, False))

        # Update Partner Bank
        if response_json.get('BankAccountNumber'):
            partner_bank_data['acc_number'] = \
                response_json['BankAccountNumber']
        bank_country_code = response_json.get('BankCountryCode', False)
        bank_country = self.env['res.country'].search(
            [('code', '=', bank_country_code)], limit=1)
        partner_bank_data['afex_bank_country_id'] = bank_country.id
        int_bank_country_code = \
            response_json.get('IntermediaryBankCountryCode', False)
        int_bank_country = self.env['res.country'].search(
            [('code', '=', int_bank_country_code)], limit=1)
        partner_bank_data['afex_int_bank_country_id'] = int_bank_country.id
        self.write(partner_bank_data)

        # Get Purpose of Payment
        Purpose = self.env['afex.purpose.of.payment']
        purpose_data = [
            ('code', '=', response_json.get('RemittanceLine2', False)),
            ('currency_id', '=', self.currency_id.id),
            ('afex_bank_country_id', '=', self.afex_bank_country_id.id),
            ('partner_country_id', '=', self.partner_country_id.id),
        ]
        purpose = Purpose.search(purpose_data, limit=1)
        if not purpose:
            self.onchange_purpose_of_payment()
            purpose = Purpose.search(purpose_data, limit=1)
        self.afex_purpose_of_payment_id = purpose.id

        # Set sync status to done
        self.afex_sync_status = 'done'

    @api.multi
    def update_afex_additional_sync_fields(self, field, value):
        self.ensure_one()
        add_info = self.add_afex_info_ids.filtered(lambda i: i.field == field)
        if not value and add_info:
            add_info.unlink()
        elif value and add_info:
            add_info.value = value
        elif value and not add_info:
            self.add_afex_info_ids = [(0, 0, {'field': field, 'value': value})]

    def return_afex_data(self):
        self.ensure_one()

        partner = self.partner_id
        # data returned for creation and updates
        data = {'Currency': self.currency_id.name or '',
                'BeneficiaryName': partner.name or '',
                'TemplateType': 1,
                'NotificationEmail': self.afex_payment_notify_email or '',
                'BeneficiaryAddressLine1': partner.street or '',
                'BeneficiaryCity': partner.city or '',
                'BeneficiaryCountryCode': partner.country_id.code or '',
                'BeneficiaryPostalCode': partner.zip or '',
                'BeneficiaryRegionCode': partner.state_id.code or '',
                'BankName': self.bank_id.name or '',
                'BankAccountNumber': self.acc_number or '',
                'BankAddress1': self.bank_id.street or '',
                'BankAddress2': self.bank_id.street2 or '',
                'BankAddress3': self.bank_id.city or '',
                'RemittanceLine1': partner.company_id.name or '',
                'RemittanceLine2': self.afex_purpose_of_payment_id.code or '',
                'HighLowValue': '1',  # default as high value

                'Corporate': self.afex_corporate,
                'BeneficiaryAddressLine2': partner.street2 or '',
                'BankCountryCode': self.afex_bank_country_id.code or '',
                'IntermediaryBankCountryCode':
                self.afex_int_bank_country_id.code or '',
                }

        # optional data - only provided if entered
        for line in self.add_afex_info_ids:
            error, value = line.validate_value()
            if value:
                data[line.field] = value

        return data


class AFEXAddFields(models.Model):
    _name = "afex.additional.sync.fields"
    _description = "AFEX Additional Sync Fields"

    bank_id = fields.Many2one('res.partner.bank', required=True,
                              ondelete='cascade')
    field = fields.Selection(AFEX_ADD_SYNC_FIELDS, required=True)
    value = fields.Char(required=True)
    active = fields.Boolean(
        compute='_compute_active',
        readonly=True,
        store=True)

    @api.depends('field')
    def _compute_active(self):
        remittanceline2 = self.filtered(lambda f: f.field == 'RemittanceLine2')
        remittanceline2.update({'active': False})
        (self - remittanceline2).update({'active': True})

    @api.multi
    @api.constrains('field', 'value')
    def _constrain_values(self):
        for addl in self:
            error, value = addl.validate_value()
            if error:
                raise UserError(error)

    @api.model
    def create(self, vals):
        result = super(AFEXAddFields, self).create(vals)
        result.mapped('bank_id').write({})
        return result

    @api.multi
    def write(self, vals):
        self.mapped('bank_id').write({})
        return super(AFEXAddFields, self).write(vals)

    @api.multi
    def unlink(self):
        self.mapped('bank_id').write({})
        return super(AFEXAddFields, self).unlink()

    def validate_value(self):
        definition = AFEX_ADD_SYNC_DEFINITION.get(self.field, {})
        max_length = definition.get('length')
        if self.value and max_length and len(self.value) > max_length:
            return (
                _('Value for "%s" is over %s chars long.')
                % (definition['name'], max_length)),\
                self.value[:max_length]
        return False, self.value or ''

    @api.onchange('field', 'value')
    def onchange_value(self):
        warnings = []
        error, value = self.validate_value()
        if error:
            warnings.append(error)
            self.value = value

        result = {}
        if warnings:
            result['warning'] = {
                'title': _('WARNING'),
                'message': '\n'.join(warnings),
                }
        return result


class AFEXPurposeOfPayment(models.Model):
    _name = 'afex.purpose.of.payment'
    _description = "AFEX Purpose of Payment"

    name = fields.Char(
        string="Description",
        required=True,
        copy=False)
    code = fields.Char(
        string="Code",
        required=True,
        copy=False)
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        copy=False)
    afex_bank_country_id = fields.Many2one(
        'res.country',
        string="AFEX Bank Country",
        required=True,
        copy=False)
    partner_country_id = fields.Many2one(
        'res.country',
        string="Beneficiary Country",
        required=True,
        copy=False)
    active = fields.Boolean(
        string="Active",
        default=True)


class ResPartner(models.Model):
    _inherit = "res.partner"

    afex_bank_ids = fields.One2many(
        'res.partner.bank',
        compute='_compute_afex_banks')
    afex_sync_status = fields.Selection(
        [('needed', 'Sync Needed'),
         ('done', 'Synchronised'),
         ('na', 'Not Applicable'),
         ],
        string='AFEX Status',
        compute='_compute_afex_sync_status'
        )

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if not self.env.context.get('sync_done') and\
                set(vals.keys()) &\
                set(['name', 'email', 'street', 'city',
                    'country_id', 'state_id', 'company_id']):
            for partner in self:
                partner.afex_bank_ids.write({'afex_sync_status': 'needed'})
        return res

    @api.one
    def _compute_afex_banks(self):
        self.afex_bank_ids = self.bank_ids.filtered(lambda b: b.is_afex)

    @api.one
    def _compute_afex_sync_status(self):
        if self.afex_bank_ids:
            self.afex_sync_status = any(
                b.afex_sync_status == 'needed' for b in self.afex_bank_ids) \
                and 'needed' or 'done'
        else:
            self.afex_sync_status = 'na'

    def afex_bank_for_currency(self, currency):
        self.ensure_one()
        return self.env['res.partner.bank'].search(
            [('partner_id', '=', self.id),
             ('is_afex', '=', True),
             ('currency_id', '=', currency.id)
             ],
            limit=1
            )

    @api.multi
    def sync_partners_afex(self):

        bank_accounts = self.env['res.partner.bank']

        for partner in self:
            if not partner.name:
                raise UserError(_(
                    'Vendor encountered with no name'))
            if not partner.supplier:
                raise UserError(_(
                    'Partner %s is not a vendor')
                    % (partner.name,))
            if not partner.company_id:
                raise UserError(_(
                    'Vendor %s is not linked to a company')
                    % (partner.name,))
            if not partner.afex_bank_ids:
                raise UserError(_(
                    'Vendor %s does not have any AFEX Beneficiary Bank'
                    ' accounts')
                    % partner.name)
            partner_banks = partner.bank_ids.filtered(
                    lambda b: b.is_afex and b.afex_sync_status == 'needed')
            if not partner_banks:
                raise UserError(_(
                    'Vendor %s does not have any Beneficiary Bank accounts'
                    ' which need to be synchronised')
                    % partner.name)
            bank_accounts |= partner_banks

        bank_accounts.sync_beneficiary_afex()
