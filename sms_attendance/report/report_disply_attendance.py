import pooler
import time
import datetime

from report import report_sxw
import netsvc
from xlrd import formula

class report_disply_attendance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
            super(report_disply_attendance, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({'get_month':self.get_month, 
                                   })
    def get_month(self,form):
        print "inside function"
        month = datetime.datetime.now().strftime("%h ,%Y")
        print "month----",month 
        return month


report_sxw.report_sxw('report.report_disply_attendance','lms.patron.registration', 
                      'addons/sms_attendance/report/report_disply_attendance_view.rml',

                      parser=report_disply_attendance,
                      header=True)