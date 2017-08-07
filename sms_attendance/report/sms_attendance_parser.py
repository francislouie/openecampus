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
        class_id = this_form['class_id'][0]
        sql = """SELECT tab1.id, tab1.name, tab1.father_name 
                FROM sms_student as tab1
                INNER JOIN sms_academiccalendar as tab2
                ON tab1.current_class = tab2.id
                WHERE tab2.id = """ + str(class_id) + """
                order by tab1.name"""
        self.cr.execute(sql)
        rows = self.cr.fetchall()
        i = 1
        for row in rows:
            result.append({'name':row[1],'father':row[2],'S.No':i})
            i += 1
        return result
     
report_sxw.report_sxw('report.smsattendance.blank.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/blank_attendance_sheet.rml', 
                        parser=sms_attendance_parser, header=None)

