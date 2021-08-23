
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class guards_payslip_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(guards_payslip_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines': self.get_payslip_lines,
        })

    def get_payslip_lines(self, obj):
        payslip_line = self.pool.get('guards.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

report_sxw.report_sxw('report.guard.payslip', 'guards.payslip', 'sos/report/report_guards_payslip.rml', parser=guards_payslip_report)

