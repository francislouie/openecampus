#-*- coding:utf-8 -*-

##############################################################################
#this parser actually replaced actaull payslip parser of module hr_payroll
##############################################################################

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class report_payslip_inherited(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_payslip_inherited, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines': self.get_payslip_lines,
        })

    def get_payslip_lines(self, obj):
        print "inherited report called lled lled called"
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

report_sxw.report_sxw('report.payslip_inherited', 'hr.payslip', 'sms_hr/report/report_payslip_inherited.rml', parser=report_payslip_inherited)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
