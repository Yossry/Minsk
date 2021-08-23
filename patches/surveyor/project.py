from odoo import fields, models


class ResCountryStateTown(models.Model):
    _name = 'res.country.state.town'
    _description = 'res.country.state.town'

    name = fields.Char('Name', required=True)
    state_id = fields.Many2one('res.country.state', 'State', required=True)


class ProjectTaskLot(models.Model):
    _name = 'project.task.lot'

    task_id = fields.Many2one('project.task', 'Task', required=True)
    lot_number = fields.Char('Lot Number', required=True)
    registration_number = fields.Char('Registration Number', required=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    file_number = fields.Char('File Number')
    plane_number = fields.Char('Plane Number')
    entry_date = fields.Date('Entre Date')
    order_date = fields.Date('Order Date')
    registration_date = fields.Date('Registration Date')
    town_id = fields.Many2one('res.country.state.town', 'Town')
    is_ccu = fields.Boolean('Is CCU?')
    lot_ids = fields.One2many('project.task.lot', 'task_id', 'Lots')
