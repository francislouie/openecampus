import time
import mx.DateTime
import datetime
from datetime import datetime
from openerp.report import report_sxw
import locale
from compiler.ast import Print
from openerp.osv import osv, fields
from openerp.tools import amount_to_text_en
 
class sms_attendance_parser(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(sms_attendance_parser, self).__init__(cr, uid, name, context)
        self.result_temp=[]
        self.localcontext.update({
            'get_today':self.get_today,
            'get_user_name':self.get_user_name,
            'get_blank_attendance_sheet':self.get_blank_attendance_sheet,
            })
        self.context = context
          
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 
     
    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return user_name
     
    def get_blank_attendance_sheet(self, data):
        result = []
        this_form = self.datas['form']
        print "-----",this_form['class_id']
#        sql = """SELECT sms_student.id FROM sms_student
#            INNER JOIN sms_academiccalendar
#            ON sms_student.admitted_to_class = sms_academiccalendar.id
#            INNER JOIN sms_classes
#            ON sms_academiccalendar.class_id = sms_classes.id 
#            WHERE sms_student.state != 'Draft'
#            AND sms_student.state != 'admission_cancel'
#            AND sms_student.state != 'drop_out'
#            AND sms_student.state != 'deleted'
#            AND registration_counter = 0
#            AND sms_classes.category = '"""+class_cat+"""'
#            AND sms_academiccalendar.session_id = """ + str(session_id) + """
#            order by admitted_on, sms_student.name"""
#            
#        self.cr.execute(sql)
#        rows = self.cr.fetchall()
        return result
     
report_sxw.report_sxw('report.smsattendance.blank.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/blank_attendance_sheet.rml', 
                        parser=sms_attendance_parser, header=None)

