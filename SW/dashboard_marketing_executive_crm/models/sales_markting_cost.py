from openerp import models, fields

class SalesMarktingCost(models.Model):
    _name = 'sales.markting.cost'
    _description = 'Sales Markting Cost'

    name = fields.Char("Name", required=True)
    date_of_investment = fields.Datetime("Date of Investment")
    cost_of_investment = fields.Float("Cost of Investment")
    campaign_id = fields.Many2one('utm.campaign', string='Campaign')
    source_id = fields.Many2one('utm.source', string='Source')
    medium_id = fields.Many2one('utm.medium', string='Medium')
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Approved')],
        string='Status',default='draft',copy=False)