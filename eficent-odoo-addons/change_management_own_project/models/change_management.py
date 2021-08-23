# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class ChangeManagementChange(models.Model):
    _inherit = 'change.management.change'

    @api.multi
    def _create_change_project(self):
        self.ensure_one()
        data = {
            'name': '%s - %s' % (self.name, self.description),
            'parent_id': self.project_id.analytic_account_id.id,
        }
        return data

    change_project_id = fields.Many2one(
        'project.project',
        string='Proposed Project',
        readonly="True",
    )

    @api.multi
    def button_create_change_project(self):
        for change in self:
            if change.change_project_id:
                raise UserError(
                    _('A Change Management Project already exists.'))
            project_data = change._create_change_project()
            project = self.env['project.project'].create(project_data)
            change.write({'change_project_id': project.id})
        return True
