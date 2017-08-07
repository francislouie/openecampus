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
            'get_filled_attendance_report_days':self.get_filled_attendance_report_days,
            'get_filled_attendance_report_recs':self.get_filled_attendance_report_recs,
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

    def get_filled_attendance_report_days(self, data):
        result = []
        this_form = self.datas['form']
        class_id = this_form['class_id'][0]
        attendance_ids = tuple(self.pool.get('sms.class.attendance').search(self.cr, self.uid, [('class_id','=',class_id)]))
        my_dict = {'date1':'', 'date2':'', 'date3':'', 'date4':'', 'date5':'', 'date6':'', 'date7':'','date8':'', 'date9':'', 'date10':''}
        i = 1
        for rec_id in attendance_ids: 
            attendance_obj = self.pool.get('sms.class.attendance').browse(self.cr, self.uid, rec_id)
            my_dict['date'+ str(i)] = attendance_obj.attendance_date
            i +=1
        result.append(my_dict)
        return result

    def get_filled_attendance_report_recs(self, data):
        result = []
        datelist = []
        this_form = self.datas['form']
        class_id = this_form['class_id'][0]
        attendance_ids = self.pool.get('sms.class.attendance').search(self.cr, self.uid, [('class_id','=',class_id)])
        attendance_objs = self.pool.get('sms.class.attendance').browse(self.cr, self.uid, attendance_ids)
        for day in attendance_objs:
            datelist.append(day.id)

        student_sql = """SELECT name, father_name, registration_no
                        FROM sms_student 
                        WHERE current_class = """ + str(class_id) + """
                        """     
        self.cr.execute(student_sql)
        studentslist = self.cr.fetchall()
        if not studentslist:
            return [{'s_no':'', 'student':'', 'date1':'', 'date2':'', 'date3':'', 'date4':'', 'date5':'', 'date6':'', 'date7':'','date8':'', 'date9':'', 'date10':''}]
                        
        k = 1
        for student in studentslist:
            my_dict = {'s_no':'', 'student':'', 'date1':'', 'date2':'', 'date3':'', 'date4':'', 'date5':'', 'date6':'', 'date7':'','date8':'', 'date9':'', 'date10':''}
            my_dict['s_no'] = k
            my_dict['student'] = student[0]
            j = 1
            for attend_id in datelist:
                get_std_att = """SELECT sms_class_attendance_lines.state FROM sms_class_attendance_lines 
                                  INNER JOIN sms_class_attendance
                                   on sms_class_attendance.id = sms_class_attendance_lines.parent_id 
                                   WHERE sms_class_attendance_lines.parent_id = """+str(attend_id)
                self.cr.execute(get_std_att)
                att_rows = self.cr.fetchone()
                if att_rows:
                    if att_rows[0] == 'Present':
                        show_status = 'P'
                       
                    elif att_rows[0] == 'Absent':
                        show_status = 'A'
                       
                    elif att_rows[0] == 'Leave':
                        show_status = 'L'  
                    my_dict['date'+str(j)] = show_status 
                else:
                    show_status = '--'                    
                    my_dict['date'+str(j)] = show_status      
                j += 1
            k += 1 
            result.append(my_dict)
        return result
     
report_sxw.report_sxw('report.smsattendance.blank.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/blank_attendance_sheet.rml', 
                        parser=sms_attendance_parser, header=None)

report_sxw.report_sxw('report.smsattendance.filled.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/filled_attendance_report.rml', 
                        parser=sms_attendance_parser, header=None)
