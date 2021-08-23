# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def button_find_or_create_address_id(self):
        partner_obj = self.env['res.partner']
        for employee in self.filtered(
                lambda e: not e.address_id and e.work_email):
            employee.address_id = partner_obj.find_or_create(
                employee.work_email)

    @api.multi
    def button_find_or_create_user_id(self):
        for employee in self.filtered(lambda e: not e.user_id):
            partner_id = (
                employee.address_id.id or
                self.env['res.partner'].find_or_create(employee.work_email))
            employee.user_id = self.env['res.users'].search([
                ('partner_id', '=', partner_id)], limit=1)
            if not employee.user_id:
                company_id = (
                    employee.company_id.id or
                    self.env['res.company']._company_default_get(
                        'res.users').id)
                employee.user_id = self.env['res.users'].create({
                    'partner_id': partner_id,
                    'login': employee.work_email,
                    'name': employee.name,
                    'phone': employee.work_phone,
                    'mobile': employee.mobile_phone,
                    'parent_id': employee.company_id.partner_id.id,
                    'company_id': company_id,
                    'company_ids': [(6, 0, [company_id])],
                }) if employee.work_email else False
            employee.address_id = partner_id
