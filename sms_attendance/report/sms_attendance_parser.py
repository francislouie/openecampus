import time
import calendar
from datetime import datetime, timedelta
from datetime import datetime
import mx.DateTime
import datetime
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
            'class_name':self.class_name,
            'get_daily_attendance_report':self.get_daily_attendance_report,
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
        datefrom = this_form['date_from']
#         dateto = this_form['date_to']

        year = int(datetime.datetime.strptime(str(datefrom), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.datetime.strptime(str(datefrom), '%Y-%m-%d').strftime('%m'))
        print"Year and month",year ,mont
        mon_days = calendar.monthrange(year,mont)[1]
        if(mont <10):
            month ='-0'+str(mont)
        else:
            month ='-'+str(mont)   
        date_from =str(str(year)+str(month)+'-01')
        date_to =str(str(year)+str(month)+'-'+str(mon_days)) 
        attendance_ids = tuple(self.pool.get('sms.class.attendance').search(self.cr, self.uid, [('class_id','=',class_id),
                                                                                                ('attendance_date','>=',date_from),
                                                                                                ('attendance_date','<=',date_to)]))
        my_dict = {'date1':'1', 'date2':'2', 'date3':'3', 'date4':'4', 'date5':'5', 'date6':'6', 'date7':'7','date8':'8','date9':'9','date10':'10','date11':'11', 'date12':'12', 'date13':'13', 'date14':'14', 'date15':'15', 'date16':'16', 'date17':'17','date18':'18','date19':'19','date20':'20','date21':'21', 'date22':'22', 'date23':'23', 'date24':'24', 'date25':'25', 'date26':'26', 'date27':'27','date28':'28','date29':'29','date30':'30','date31':'31'}
        i = 1
        for rec_id in attendance_ids: 
            attendance_obj = self.pool.get('sms.class.attendance').browse(self.cr, self.uid, rec_id)
            attendance_date= attendance_obj.attendance_date
            date_attendace = int(datetime.datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%d'))
#             if date_attendace!=i:
#                 my_dict['date'+ str(i)] = date_attendace
#             else:
#                 my_dict['date'+ str(i)] = '--'
# 
#             i +=1
        result.append(my_dict)
        return result

    def class_name(self, form): 

        this_form = self.datas['form']
        class_id = this_form['class_id'][0]
        datefrom = this_form['date_from']
        month = int(datetime.datetime.strptime(str(datefrom), '%Y-%m-%d').strftime('%m'))
        if month == 1:
            MonthN = "January"
        elif  month == 2:
            MonthN =  "February"
        elif  month == 3:
            MonthN =  "March"
        elif  month == 4:
            MonthN =  "April"
        elif  month == 5:
            MonthN =  "May"
        elif  month == 6:
            MonthN =  "June"
        elif  month == 7:
            MonthN =  "July"
        elif  month == 8:
            MonthN =  "August"
        elif  month == 9:
            MonthN =  "September"
        elif  month == 10:
            MonthN =  "October"
        elif  month ==11:
            MonthN =  "November"
        elif  month == 12:
            MonthN =  "December"
            
        result= self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, class_id).name +' '+'For the month of'+'  '+str(MonthN)
        return result
    
    
    
    
# method is calling from here 
    def get_filled_attendance_report_recs(self, data):
        print"get_filled_attendance_report_recs"
        result = []
        datelist = []
        this_form = self.datas['form']
        class_id = this_form['class_id'][0]
        datefrom = this_form['date_from']
#         datefrom ='2017-12-01'
#         dateto = this_form['date_to']

        year = int(datetime.datetime.strptime(str(datefrom), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.datetime.strptime(str(datefrom), '%Y-%m-%d').strftime('%m'))
        print"Year and month",year ,mont
        mon_days = calendar.monthrange(year,mont)[1]
        if(mont <10):
            month ='-0'+str(mont)
        else:
            month ='-'+str(mont)   
        date_from =str(str(year)+str(month)+'-01')
        date_to =str(str(year)+str(month)+'-'+str(mon_days))

        attendance_ids = self.pool.get('sms.class.attendance').search(self.cr, self.uid, [('class_id','=',class_id),
                                                                                          ('attendance_date','>=',date_from),
                                                                                          ('attendance_date','<=',date_to)])
        attendance_objs = self.pool.get('sms.class.attendance').browse(self.cr, self.uid, attendance_ids)
        for attend in attendance_objs:
            datelist.append(attend.id)
        student_sql = """SELECT name, father_name, registration_no, id
                        FROM sms_student 
                        WHERE current_class = """ + str(class_id) + """
                        """     
        self.cr.execute(student_sql)
        studentslist = self.cr.fetchall()
        if not studentslist:
            return [{'s_no':'', 'student':'','date1':'', 'date2':'', 'date3':'', 'date4':'', 'date5':'', 'date6':'', 'date7':'','date8':'','date9':'','date10':'','date11':'', 'date2':'', 'date13':'', 'date14':'', 'date15':'', 'date16':'', 'date17':'','date18':'','date19':'','date20':'','date21':'', 'date22':'', 'date23':'', 'date24':'', 'date25':'', 'date26':'', 'date27':'','date28':'','date29':'','date30':'','date31':''}]
                        
        i = 1
        for student in studentslist:
            my_dict = {'s_no':'', 'student':'', 'date1':'--', 'date2':'--', 'date3':'--', 'date4':'--', 'date5':'--', 'date6':'--', 'date7':'--','date8':'--','date9':'--','date10':'--','date11':'--', 'date12':'--', 'date13':'--', 'date14':'--', 'date15':'--', 'date16':'--', 'date17':'--','date18':'--','date19':'--','date20':'--','date21':'--', 'date22':'--', 'date23':'--', 'date24':'--', 'date25':'--', 'date26':'--', 'date27':'--','date28':'--','date29':'--','date30':'--','date31':'--'}
            my_dict['s_no'] = i
            my_dict['student'] = student[0]
            j = 1
            for attend_id in datelist:
                atten_date = """SELECT attendance_date FROM sms_class_attendance  WHERE id = """+str(attend_id)
                self.cr.execute(atten_date)
                Date_attendance = self.cr.fetchone()[0]
                day = int(datetime.datetime.strptime(str(Date_attendance), '%Y-%m-%d').strftime('%d'))
                get_std_att = """SELECT state FROM sms_class_attendance_lines 
                                WHERE student_name = """+str(student[3])+"""
                                AND parent_id = """+str(attend_id)
                self.cr.execute(get_std_att)
                att_rows = self.cr.fetchone()
                if not att_rows:
                    get_std_att_alternate_qry = """SELECT state, present, absent, leave, student_name 
                                    FROM sms_class_attendance_lines 
                                    WHERE student_name = """+str(student[3])+"""
                                    AND parent_id = """+str(attend_id)
                    self.cr.execute(get_std_att_alternate_qry)
                    att_rows = self.cr.fetchone()
                    
                if att_rows:    
                    if att_rows[0] == 'Present':
                        show_status = 'p'
                       
                    elif att_rows[0] == 'Absent':
                        show_status = 'A'
                       
                    elif att_rows[0] == 'Leave':
                        show_status = 'L'
                    my_dict['date'+str(day)] = show_status 
                else:
                    show_status = '--'                    
                    my_dict['date'+str(day)] = show_status      
                j += 1
            i += 1 
            result.append(my_dict)
        return result
     #end 
    def get_daily_attendance_report(self, data):
        result = []
        final_dict = {}
        this_form = self.datas['form']
        session_id = this_form['session_id'][0]
        date_str = this_form['date']

        date = datetime.strptime(str(date_str), '%Y-%m-%d')

        session_obj = self.pool.get('sms.session').browse(self.cr, self.uid, session_id)

        final_dict.update({'date': date.strftime('%d-%m-%Y')})
        final_dict.update({'day': date.strftime('%A')})
        final_dict.update({'session': session_obj.academic_session_id.name})
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(self.cr, self.uid, [('session_id','=',session_id)])
        academiccalendar_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, academiccalendar_ids)
        
        total_students = 0
        total_presents = 0
        total_absents = 0
        total_leaves = 0
        attendances = []
        for i, k in enumerate(academiccalendar_obj):
            my_dict = {'s_no':'', 'class':'', 'section':'', 'total_students':'', 'present':'', 'absent':'', 'leave':''}
            my_dict['s_no'] = i + 1
            my_dict['class'] = k.class_id.name
            my_dict['section'] = k.section_id.name
            my_dict['class_students'] = k.cur_strength
            

            class_attendance = k.get_class_attendance(k.id, date.date())
            
            total_students += k.cur_strength
            total_presents += class_attendance['present']
            total_absents += class_attendance['absent']
            total_leaves += class_attendance['leave']

            my_dict['present'] = class_attendance['present']
            my_dict['absent'] = class_attendance['absent']
            my_dict['leave'] = class_attendance['leave']

            attendances.append(my_dict)

        final_dict.update({'attendances': attendances})

        final_dict.update({'total_students': total_students})
        final_dict.update({'total_presents': total_presents})
        final_dict.update({'total_absents': total_absents})
        final_dict.update({'total_leaves': total_leaves})

        final_dict.update({'date_printed': datetime.now().strftime('%d-%m-%Y')})
        final_dict.update({'printed_by': self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name})

        result.append(final_dict)
        return result
        
        # for i in academiccalendar_ids:
        #     result.append({'class':"Aadam",'section':date,'s_no':i})
        # return result

report_sxw.report_sxw('report.smsattendance.blank.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/blank_attendance_sheet.rml', 
                        parser=sms_attendance_parser, header='external')

report_sxw.report_sxw('report.smsattendance.filled.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/filled_attendance_report.rml', 
                        parser=sms_attendance_parser, header='external')

report_sxw.report_sxw('report.smsattendance.daily.attendance.sheet',
                        'sms.academiccalendar',
                        'addons/sms_attendance/report/daily_attendance_report.rml', 
                        parser=sms_attendance_parser, header=None)
