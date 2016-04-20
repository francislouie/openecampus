import pooler
import time
import datetime
from openerp.report import report_sxw

class report_disply_attendance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_disply_attendance, self).__init__(cr, uid, name, context = context)
        self.result_temp=[]
        self.localcontext.update( { 'print_form': self.print_form,
        })
        self.context = context
    
    def print_form(self,form):
        print "inside function"
        month = datetime.datetime.now().strftime("%h ,%Y")
        print "month----",month
        return month
    
    
report_sxw.report_sxw('report.report_disply_attendance','sms.class.attendance', 
                      'addons/sms_attendance/report/report_disply_attendance_view.rml',
                      parser=report_disply_attendance,
                      header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

