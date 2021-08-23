# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    center_ids = fields.Many2many(
        comodel_name='res.partner', string='Education Centers',
        compute='_compute_center_ids', store=True)
    tutored_student_ids = fields.One2many(
        comodel_name='hr.employee.supervised.year',
        inverse_name='teacher_id', string='Tutored students per year')
    count_tutored_students = fields.Integer(
        string='# Tutored students', compute='_compute_count_tutored_students')

    @api.depends('user_id', 'user_id.school_ids')
    def _compute_center_ids(self):
        for employee in self.filtered('user_id'):
            employee.center_ids = employee.user_id.school_ids

    @api.depends('tutored_student_ids')
    def _compute_count_tutored_students(self):
        for employee in self:
            employee.count_tutored_students = (
                len(employee.tutored_student_ids))

    @api.multi
    def button_show_tutored_students(self):
        self.ensure_one()
        self = self.with_context(
            search_default_teacher_id=self.id, default_teacher_id=self.id)
        action = self.env.ref(
            'hr_school.action_hr_employee_supervised_year_form')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update(
            {'search_default_teacher_id': self.id,
             'default_teacher_id': self.id})
        domain = expression.AND([
            [('teacher_id', '=', self.id)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict


class HrEmployeeSupervisedYear(models.Model):
    _name = 'hr.employee.supervised.year'
    _description = 'Tutored by year'

    school_year_id = fields.Many2one(
        string='School year', comodel_name='education.academic_year',
        required=True)
    teacher_id = fields.Many2one(
        string='Teacher', comodel_name='hr.employee',
        required=True)
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        required=True)
    center_id = fields.Many2one(
        string='Education Center', comodel_name='res.partner')
    user_id = fields.Many2one(
        string='User', comodel_name='res.users', store=True,
        related='teacher_id.user_id')

    @api.multi
    def name_get(self):
        result = []
        for year in self:
            name = _(
                u"Academic year: {}, teacher: {}, student: {}").format(
                    year.school_year_id.name, year.teacher_id.name,
                    year.student_id.name)
            result.append((year.id, name))
        return result
