# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.tools import UserError
import logging

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one(string='Project', comodel_name="project.project")
    task_id = fields.Many2one(string='Task', comodel_name="project.task")

    @api.one
    def create_timereport(self):
        # ~ if not self.project_id:
                # ~ raise UserError(_('You have to at least add a Project'))
        for partner in self.partner_ids:
            
            user = self.env['res.users'].search([('partner_id','=',partner.id)])
            if user:
                employee = self.env['hr.employee'].search([('user_id','=',user.id)])
            if employee:
                sheet = self.env['hr_timesheet.sheet'].search([('employee_id','=', employee.id),
                                                            ('date_start', '<=', self.start_datetime.date()), 
                                                            ('date_end', '>=', self.start_datetime.date())])
                if not sheet:
                    #TODO: this defaults to current week/month, this only works if there is a time_sheet for other weeks 
                    sheet = self.env['hr_timesheet.sheet'].create({'employee_id':employee.id}) 
                timereport = self.env['account.analytic.line'].create({
                    'date': self.start_datetime.date(),
                    'name': self.name,
                    'partner_id': partner.id,
                    'project_id': self.project_id.id if self.project_id else None,
                    'task_id': self.task_id.id if self.task_id else None,
                    'unit_amount': self.duration,
                    'sheet_id': sheet.id,
                    'employee_id': employee.id,
                    'account_id': self.project_id.analytic_account_id.id,
                })
        

