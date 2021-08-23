# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools ,_
from odoo.exceptions import except_orm, ValidationError,UserError
from odoo.exceptions import  AccessError, UserError, RedirectWarning,Warning
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta , date
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.exceptions
import re 
from odoo.http import request
from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
from ast import literal_eval
from odoo.addons.web.controllers.main import clean_action

class ProjectSubTask(models.Model):
    _inherit = "project.task"

    module_name = fields.Many2one('ir.module.module',string='Module Name',track_visibility='onchange')
    task_type = fields.Many2one('task.type',string="Type")
    scope_status = fields.Selection([
            ('include', 'Included in the scope'),
            ('out', 'Out of the scope(additional)')], string='Scope Status', track_visibility='onchange',
            default='include', copy=False)
    estimated_efforts = fields.Float('Estimated Efforts')
    customer_owner = fields.Char('Customer Ownership')
    internal_notes = fields.Text('Internal Notes')
    external_notes = fields.Text('External Notes')

class TaskType(models.Model):
    _name = "task.type"

    name = fields.Char('Name')

class IssueLog(models.Model):
    _name = "issue.log"
    # _inherit = ''

    Project_name = fields.Many2one('project.project',string="Project")
    complexity = fields.Selection([
            ('low', 'Low'),
            ('med', 'Medium'),
            ('high', 'High')], string='Complexity',
            default='low', copy=False)
    status = fields.Selection([
            ('wip', 'WIP'),
            ('testing', 'Internal testing'),
            ('completed', 'Completed')  ], string='Status',
            default='wip', copy=False)
    raised_date = fields.Date('Raised Date')
    planned_date = fields.Date('Planned Date')
    completed_date = fields.Date('Completed Date')
    module_name = fields.Many2one('ir.module.module',string='Module Name')
    assigned_to = fields.Many2one('res.users',string='Assigned to')
    issue_detail = fields.Text('Issue Details')
    internal_notes = fields.Text('Internal Notes')
    external_notes = fields.Text('External Notes')



   
    