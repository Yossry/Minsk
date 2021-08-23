# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class AssetDisposalReport(models.Model):
    _name = 'asset.disposal.report'
    _auto = False
    
    name = fields.Char(string='Year', required=False, readonly=True)
    date = fields.Date(readonly=True)
    depreciation_date = fields.Date(string='Depreciation Date', readonly=True)
    asset_id = fields.Many2one('account.asset.asset.custom', string='Asset', readonly=True)
    asset_category_id = fields.Many2one('account.asset.category.custom', string='Asset category', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'), ('close', 'Close')], string='Status', readonly=True)
    depreciation_value = fields.Float(string='Amount of Depreciation Lines', readonly=True)
    installment_value = fields.Float(string='Amount of Installment Lines', readonly=True)
    move_check = fields.Boolean(string='Posted', readonly=True)
    installment_nbr = fields.Integer(string='# of Installment Lines', readonly=True)
    depreciation_nbr = fields.Integer(string='# of Depreciation Lines', readonly=True)
    gross_value = fields.Float(string='Gross Amount', readonly=True)
    posted_value = fields.Float(string='Posted Amount', readonly=True)
    unposted_value = fields.Float(string='Unposted Amount', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    residual_value = fields.Float(
        string='Residual Value',
    )
    depreciation = fields.Float(
        string='Depreciation',
    )
    accumulated_depreciation = fields.Float(
        string='Accumulated Depreciation',
    )
    number_asset = fields.Float(
        string='Number of Assets',
    )
    number = fields.Char(
        string='Asset Sequence Number',
    )
#     asset_period = fields.Integer(
#         string="Period",
#         default=0
#     )
    active = fields.Boolean(
        string = "Active"
    )
    diposal_type = fields.Selection(
        [('sale', 'Sale'),
         ('write_off', 'Write-Off')],
        string='Disposal Type',
    )

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'asset_disposal_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW asset_disposal_report AS (
                select
                    min(dl.id) as id,
                    dl.name as name,
                    dl.depreciation_date as depreciation_date,
                    a.date as date,
                    a.custom_number as number,
                    (CASE WHEN dlmin.id = min(dl.id)
                      THEN a.value
                      ELSE 0
                      END) as gross_value,
                    dl.amount as depreciation_value,
                    dl.amount as installment_value,
                    dl.amount as residual_value,
                    dl.amount as depreciation,
                    dl.amount as accumulated_depreciation,
                    dl.amount as number_asset,
                    (CASE WHEN dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as posted_value,
                    (CASE WHEN NOT dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as unposted_value,
                    dl.asset_id as asset_id,
                    dl.move_check as move_check,
                    a.category_id as asset_category_id,
                    a.partner_id as partner_id,
                    a.state as state,
                    count(dl.*) as installment_nbr,
                    count(dl.*) as depreciation_nbr,
                    a.company_id as company_id,
                    a.active as active,
                    a.diposal_type as diposal_type
                from account_asset_depreciation_line_custom dl
                    left join account_asset_asset_custom a on (dl.asset_id=a.id)
                    left join (select min(d.id) as id,ac.id as ac_id from account_asset_depreciation_line_custom as d inner join account_asset_asset_custom as ac ON (ac.id=d.asset_id) group by ac_id) as dlmin on dlmin.ac_id=a.id
                where
                    a.use_disposal IS TRUE
                group by
                    dl.amount,dl.asset_id,dl.depreciation_date,dl.name,
                    a.date, dl.move_check, a.state, a.category_id, a.partner_id, a.company_id, a.custom_number,
                    a.value, a.id, a.salvage_value, dlmin.id
            )""")




