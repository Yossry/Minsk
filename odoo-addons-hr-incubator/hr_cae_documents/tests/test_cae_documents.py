# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCAEDocuments(TransactionCase):
    def test_copy_documents(self):
        applicant = self.browse_ref("hr_recruitment.hr_case_salesman0")
        self.assertEquals(len(applicant.attachment_ids), 1)
        applicant.create_employee_from_applicant()
        self.assertEquals(len(applicant.emp_id.document_ids), 1)
