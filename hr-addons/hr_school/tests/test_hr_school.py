# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _
from odoo.tests import common


class TestHrSchool(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrSchool, cls).setUpClass()
        year_vals = {
            'name': '2019+2020',
            'date_start': '2019-09-01',
            'date_end': '2020-06-30',
        }
        cls.year = cls.env['education.academic_year'].create(year_vals)
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Teacher',
            'user_id': cls.env.ref('base.user_admin').id,
        })
        # cls.employee.user_id = cls.env.ref('base.user_admin')
        cls.student = cls.env['res.partner'].create({
            'name': 'Student',
            'educational_category': 'student',
        })
        tutored_vals = {
            'school_year_id': cls.year.id,
            'teacher_id': cls.employee.id,
            'student_id': cls.student.id,
        }
        cls.tutored = cls.env['hr.employee.supervised.year'].create(
            tutored_vals)

    def test_hr_school(self):
        self.assertEqual(self.employee.count_tutored_students, 1)
        res = self.employee.button_show_tutored_students()
        domain = [('teacher_id', '=', self.employee.id)]
        self.assertEqual(res.get('domain'), domain)
        self.assertEqual(self.student.allowed_user_ids, self.employee.user_id)
        lit = _(u"Academic year: {}, teacher: {}, student: {}").format(
            self.tutored.school_year_id.name, self.tutored.teacher_id.name,
            self.tutored.student_id.name)
        self.assertIn(lit, self.tutored.display_name)
