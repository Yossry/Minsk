# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class TicketQuotation(models.Model):
    _name = 'ticket.quotation'
    _description = 'Ticket Quotation'

    name = fields.Char(string='Description')
    partner_id = fields.Many2one('res.partner', string='Agent')
    ticket_id = fields.Many2one('air.ticket.request', string='Ticket')
    product_id = fields.Many2one('product.product', string='Product')
    cost = fields.Float(string='Ticket Cost')
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    reason = fields.Text(string='Reason for selection')

    @api.multi
    def action_approve(self):
        self.ensure_one()
        self.write({'state': 'approved'})
        rejected_quote = self.search([('id', 'not in', self.ids)])
        rejected_quote.write({'state': 'rejected'})
        self.ticket_id.approved_quote_id = self.id
        return True


class AirTicketRequest(models.Model):
    _name = 'air.ticket.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Air Ticket Request'

    name = fields.Text(string='Description')
    start_point = fields.Char(string='Start Point(City)')
    end_point = fields.Char(string='End Point(City)')
    date = fields.Date(string='Travel Date')
    prefer_travel_time = fields.Selection([
        ('Morning', 'Morning'),
        ('Day', 'Day'),
        ('Evening', 'Evening'),
        ('Night', 'Night')], string='Prefer Travel Time')
    note = fields.Text('Meal Preference')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    leave_id = fields.Many2one('hr.leave', string='Leave', required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='State', default='draft')
    leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Air Ticket Agent')
    partner_ids = fields.Many2many('res.partner', 'res_partner_air_ticket_id', string='Air Ticket Agent', domain=[('is_travel_agent', '=', True)])
    quote_ids = fields.One2many('ticket.quotation', 'ticket_id', string='Travel Cost Quotes')
    approved_quote_id = fields.Many2one('ticket.quotation', string='Approved Quotation')

    @api.constrains('leave_type_id')
    def check_allow_ticket_request(self):
        for ticket in self:
            if ticket.leave_type_id.air_ticket and self.search_count([('employee_id', '=', ticket.employee_id.id)]) > ticket.leave_type_id.no_of_ticket_allowed:
                raise ValidationError(_('You can not create an air ticket for this leave type as it reach to maximum ticket allow on this leave type.'))

    @api.onchange('partner_ids')
    def onchange_partner_ids(self):
        if self.partner_ids:
            self.quote_ids = [(0, 0, {'partner_id': p.id, 'state': 'pending'}) for p in self.partner_ids]

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.activity_schedule(
            'qpr_hr.mail_act_air_ticket_approval',
            user_id=self.env.user.company_id.hr_manager_id.user_id.id)
        return self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        self.activity_feedback(['qpr_hr.mail_act_air_ticket_approval'])
        return self.write({'state': 'approved'})

    @api.multi
    def action_reject(self):
        self.activity_feedback(['qpr_hr.mail_act_air_ticket_approval'])
        return self.write({'state': 'rejected'})

    @api.multi
    def action_send_mail_to_agent(self):
        self.ensure_one()
        # TODO - Add mail template
        template_id = self.env.ref('qpr_hr.email_template_air_ticket').id
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'air.ticket.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_subtype_id': self.env.ref('mail.mt_note').id,
            'default_partner_ids': self.partner_ids.ids,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

##########################################

# And then HR Manager Can able to see the AIR-Ticket Request Along with the Leave Request.
# Then HR Manager can able to send (Mail, based on given details) Ticket Pricing request to
# Travel Agent(defined in our system as Vendor), select the vendor and send mail for ticket request.
# Once HR get mail back from vendor for ticket she will find judge right ticket and then add ticket
# with the Leave request and approve for Final. So all person (Department Manager and Employee will get mail of
# Final Leave Confirmation).

# Once Ticket is confirmed no once change it ticket must need t linked with a vendor ID later discuss on the flow.
###########################################

