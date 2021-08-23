from odoo import fields, models


class ResCountryStateTown(models.Model):
    _name = 'res.country.state.town'
    _description = 'res.country.state.town'
    name = fields.Char('Name', required=True)
    state_id = fields.Many2one('res.country.state', 'State', required=True)


class AccountAnalyticAccountLot(models.Model):
    _name = 'account.analytic.account.lot'
    _description = 'account.analytic.account.lot'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Project/Contract', required=True)
    lot_number = fields.Char('Lot Number', required=True)
    registration_number = fields.Char('Registration Number', required=True)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    file_number = fields.Char('File Number')
    plane_number = fields.Char('Plane Number')
    entry_date = fields.Date('Entre Date')
    order_date = fields.Date('Order Date')
    registration_date = fields.Date('Registration Date')
    town_id = fields.Many2one('res.country.state.town', 'Town')
    is_ccu = fields.Boolean('Is CCU?')
    lot_ids = fields.One2many(
        'account.analytic.account.lot', 'analytic_account_id', 'Lots')
