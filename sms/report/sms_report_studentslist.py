import time
import datetime
from datetime import date
import logging
_logger = logging.getLogger(__name__)
from openerp.report import report_sxw

class sms_report_studentslist(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_studentslist, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'report_title': self.report_title,
            'class_name': self.class_name,
            'get_student_contacts': self.get_student_contacts,
            'get_admission_statistics': self.get_admission_statistics,
            'print_students_class_list':self.print_students_class_list,
            'get_student_biodata' : self.get_student_biodata,
            'get_withdrawn_student_info':self.get_withdrawn_student_info,
            'print_student_se_passes':self.print_student_se_passes,
            'get_student_strength':self.get_student_strength,            
            'get_date_range':self.get_date_range,
            'get_student_strength_message':self.get_student_strength_message,
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        start_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['start_date'])
        end_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['end_date'])
        string = "Students Admissions \n " +str(start_date) + "-TO -"+str(end_date)
        return string
    
    def class_name(self, form): 
        if form['class_form']:
            acad_cal = form['class_id'][0]
        else:
            acad_cal = form['acad_cal'][0]
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, acad_cal).name
    
    def get_student_contacts(self, data):                                                         
        result = []
        this_form = self.datas['form']
        acad_cal = this_form['acad_cal'][0]
        
        students = """SELECT registration_no,name,father_name,birthday,cell_no,phone
                          FROM sms_student WHERE current_class ="""+str(acad_cal)+"""
                          AND state not in('admission_cancel','drop_out','deleted','slc') ORDER BY name"""
        self.cr.execute(students)
        rows = self.cr.fetchall() 
        i = 1
        for row in rows:
            mydict = {'sno':'','admsn_no':'','student':'','father':'','Cellno':'--','phone':'--',}
            mydict['sno'] = i
            mydict['admsn_no'] = row[0]
            mydict['student'] = row[1]
            mydict['father'] = row[2]
            if row[3]:
                mydict['dob'] =  datetime.datetime.strptime(str(row[3]),'%Y-%m-%d').strftime('%d-%m-%Y')
            mydict['Cellno'] = row[4]
            mydict['phone'] = row[5]
            i = i + 1
            result.append(mydict)
        return result

    def get_student_strength_message(self, form):                                                         
        this_form = self.datas['form']
        draft_boolean = this_form['display_draft_waitapprov']
        if draft_boolean is True:
            return 'The total sum of current students shows sum of all stdudents in Draft, Waiting Approval and Current State'
        else:
            return ''

    def get_student_strength(self, form):                                                         
        result = []
        this_form = self.datas['form']
        draft_boolean = this_form['display_draft_waitapprov']
        class_ids = self.pool.get('sms.academiccalendar').search(self.cr, self.uid, [('state','=','Active')], order='disp_order, section_id')
        class_objs = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, class_ids)
        i = 1
        total_cur_strength = 0
        total_allowed_students = 0        
        for class_obj in class_objs:
            mydict = {'s_no':'', 'class':'', 'strength':''}
            draft_stds = self.pool.get('sms.academiccalendar').count_students_admission_draft(self.cr, self.uid, class_obj.id)
            wait_approv_stds = self.pool.get('sms.academiccalendar').count_students_admission_wait_approval(self.cr, self.uid, class_obj.id)
            mydict['s_no']  = i
            mydict['class']     = class_obj.name
            if draft_boolean is True:
                total_cur_strength = total_cur_strength + class_obj.cur_strength + draft_stds + wait_approv_stds  
            else:
                total_cur_strength = total_cur_strength + class_obj.cur_strength
            mydict['strength']  = class_obj.cur_strength
            total_allowed_students = total_allowed_students + class_obj.max_stds            
            i += 1
            result.append(mydict)
            
        mydict = {'s_no':'', 'class':'', 'strength':''}
        mydict['class']     = 'Total Students'
        mydict['strength']  = total_cur_strength
        result.append(mydict)
        return result
    
    def get_withdrawn_student_info(self,form):                                                         
        result = []
        this_form = self.datas['form']
        acad_cal = this_form['acad_cal'][0]
        get_student_ids = self.pool.get('sms.academiccalendar').get_withdrawn_students(self.cr, self.uid, acad_cal)
        if get_student_ids:
            i = 1
            for student in get_student_ids:
                mydict = {'s_no':'', 'name':'', 'class':'', 'admission_date':'', 'withdraw_date':'','withdraw_by':'', 'approved_by':''}
                student_obj = self.pool.get('sms.student').browse(self.cr, self.uid, student)
                mydict['s_no'] = i
                mydict['name'] = student_obj.name
                mydict['class'] = student_obj.current_class.name
                mydict['admission_date'] = student_obj.admitted_on
                mydict['withdraw_date'] = student_obj.date_withdraw
                mydict['withdraw_by'] = student_obj.withdraw_by.name
                mydict['approved_by'] = ''
                i += 1
                result.append(mydict)
        return result
  
    def print_students_class_list(self, form):                                                         
        result = []
        if form['class_form']:
            acad_cal = form['class_id'][0]
        else:
            acad_cal = form['acad_cal'][0]
        students = """SELECT registration_no,name,father_name,birthday,cell_no,phone
                          FROM sms_student WHERE current_class ="""+str(acad_cal)+"""
                          AND state not in('admission_cancel','drop_out','deleted','slc') ORDER BY name"""
        self.cr.execute(students)
        rows = self.cr.fetchall() 
        i = 1
        for row in rows:
            mydict = {'sno':'','admsn_no':'','student':'','father':''}
            mydict['sno'] = i
            mydict['admsn_no'] = row[0]
            mydict['student'] = row[1]
            mydict['father'] = row[2]
            i = i + 1
            result.append(mydict)
        return result

    def get_date_range(self, form): 
        return "Admissions From: "+str(form['start_date'])+" To: "+str(form['end_date'])
    
    def get_admission_statistics(self, data):
        result = []
        fslist = []
        this_form = self.datas['form']
        fee_st =tuple(self.pool.get('sms.feestructure').search(self.cr, self.uid, []))
        _logger.info("_______ %r out of_________", (fee_st))
        i = 1
        #-------------- Setting Fee Structure Label Table for Report -----------------------------        
        my_dict = {'s_no':'#', 'acad_cal':'Class', 'state':'State', 'fs1':'', 'fs2':'', 'fs3':'', 'fs4':'', 'fs5':'', 'fs6':'', 'withdrawals':'Withdrawals', 'total_stds':'Total Students'}
        for fs in fee_st:
            recfee_st  = self.pool.get('sms.feestructure').browse(self.cr, self.uid, fs)
            sql_checking = """
                            SELECT COUNT(sms_student.id) 
                            FROM sms_student
                            WHERE sms_student.fee_type = """+str(recfee_st.id)+"""
                            AND sms_student.state in ('Admitted','admission_cancel','drop_out','slc') 
                            AND sms_student.admitted_on BETWEEN '""" + this_form['start_date'] + """' AND '""" + this_form['end_date'] + """'"""
            
            self.cr.execute(sql_checking)
            feestructure = self.cr.fetchone()
            
            if feestructure[0] == 0:
                continue
            my_dict['fs'+ str(i)] = recfee_st.name
            fslist.append(recfee_st.id)
            i = i +1
            
        result.append(my_dict)
#        sql = """SELECT id ,name ,state FROM sms_academiccalendar ORDER BY name"""
        sql = """SELECT DISTINCT tab2.id, tab2.name, tab2.state, tab1.state 
                FROM student_admission_register as tab1
                INNER JOIN sms_academiccalendar as tab2
                ON tab1.student_class = tab2.id
                WHERE tab1.date_admission_confirmed BETWEEN '""" + this_form['start_date'] + """' AND '""" + this_form['end_date'] + """' 
                AND tab1.state = 'Confirm'"""
                
        self.cr.execute(sql)
        acad_cal = self.cr.fetchall()
        j = 1

        #-------------- Getting All Classes -----------------------------        
        for cls in acad_cal:
            my_dict = {'s_no':'', 'acad_cal':'', 'state':'', 'fs1':'', 'fs2':'', 'fs3':'','fs4':'','fs5':'', 'fs6':'', 'total_stds':''}            
            my_dict['s_no'] = j
            my_dict['acad_cal'] = cls[1]
            my_dict['state'] = cls[2]
            j +=1
            k = 1
            my_dict['total_stds'] = 0
            
            #-------------- Checking admitted students in the specified date range -----------------------------
            count_per_fs = 0       
            for fs in fslist:
                
                sql = """SELECT COUNT(sms_student.id) 
                    FROM sms_student
                    INNER JOIN sms_academiccalendar_student 
                    ON sms_student.id = sms_academiccalendar_student.std_id
                    WHERE sms_student.current_class = """ + str(cls[0]) + """ 
                    AND sms_student.fee_type = """ + str(fs) + """
                    AND sms_student.state in ('Admitted','admission_cancel','drop_out','slc')
                    AND sms_student.admitted_on BETWEEN '""" + this_form['start_date'] + """' AND '""" + this_form['end_date'] + """'"""
                    
                self.cr.execute(sql)
                row = self.cr.fetchone()
                my_dict['fs'+str(k)] =  row[0]
                my_dict['total_stds'] = my_dict['total_stds'] + row[0] 
                k = k +1
            result.append(my_dict)
            
            #------------ Withdrawals --------------#
            sql = """SELECT COUNT(sms_student.id) 
                    FROM sms_student
                    INNER JOIN sms_academiccalendar_student 
                    ON sms_student.id = sms_academiccalendar_student.std_id
                    WHERE sms_student.current_class = """ + str(cls[0]) + """ 
                    AND sms_student.state in ('Admitted','admission_cancel','drop_out','slc')
                    AND sms_student.date_withdraw BETWEEN '""" + this_form['start_date'] + """' AND '""" + this_form['end_date'] + """'"""
                    
            self.cr.execute(sql)
            row = self.cr.fetchone()
            my_dict['withdrawals'] =  row[0]
            
        return result
    
    def get_student_biodata(self,form):
        
        sql = """update sms_academiccalendar set display_order = (select sequence from sms_classes where
             id = (select sms_academiccalendar.class_id))"""
        self.cr.execute(sql)
        self.cr.commit()
         
        #------  To Populate admission confirmation date in student_admission_register object ------------------
        sql = """SELECT sms_student.id, sms_student.admitted_on, student_admission_register.id
                FROM sms_student
                INNER JOIN student_admission_register
                ON sms_student.admission_form_no = student_admission_register.id
                """
        self.cr.execute(sql)
        studentrecs = self.cr.fetchall()
         
        # now reset order of smsfee_studentfee
        fees = self.pool.get('smsfee.studentfee').search(self.cr, self.uid, [])
        feerec = self.pool.get('smsfee.studentfee').browse(self.cr, self.uid,fees)
        for thisfee in feerec:
            if thisfee.fee_type is not None:
                if thisfee.fee_type.fee_type is not None:
                    self.pool.get('smsfee.studentfee').write(self.cr, self.uid, thisfee.id, {'display_order':thisfee.fee_type.fee_type.display_sequence})
         
        for rec in studentrecs:
            updating = self.pool.get('student.admission.register').write(self.cr, self.uid, rec[2], {'date_admission_confirmed':rec[1]})
            if updating:
                print 'success'
                
        #-----------Update login Ids for students----------------------------
#         sql_query = """SELECT campus_code from res_company"""
#         self.cr.execute(sql_query)
#         campus_code = self.cr.fetchone()
#         student_ids = self.pool.get('sms.student').search(self.cr, self.uid, [])
#         srudent_recs = self.pool.get('sms.student').browse(self.cr, self.uid, student_ids)
#         for rec in srudent_recs:
#             registration_no = rec.registration_no
#             login_id = str(campus_code[0])+str(registration_no)
#             import random
#             random_pass = random.randrange(100, 1000)
#             password = str(random_pass)+str(registration_no)
#             update=self.pool.get('sms.student').write(self.cr, self.uid, rec.id, {'login_id':login_id, 'password':password})
#             if update:
#                 print 'Done'
                
#        temporary query to set students security fee
        sql0 = """SELECT smsfee_studentfee.id,student_id,receipt_no,paid_amount FROM smsfee_studentfee
              inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
              inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
            WHERE smsfee_feetypes.refundable = True  and smsfee_studentfee.state = 'fee_paid'"""
        self.cr.execute(sql0)
        feeids = self.cr.fetchall()
        if feeids:
            for booklines_rw in feeids:
              
                addfee = self.pool.get('smsfee.studentfee.refundable').create(self.cr,self.uid,{
                                        'student_id':booklines_rw[1],
                                        'receipt_no':booklines_rw[2],
                                        'amount_received':booklines_rw[3],
                                        'amount_paid_back':0,
                                        'student_fee_id':booklines_rw[0],
                                        'state':'to_be_paid'})
        
        res = []
        s_no = 0
        _ids = self.pool.get('sms.academiccalendar.student').search(self.cr ,self.uid ,[('name','=',form['acad_cal'][0])])
        std_t = tuple(_ids)
        sql = """SELECT std_id FROM sms_academiccalendar_student
            WHERE id IN """+str(std_t)+""" """
        self.cr.execute(sql)
        
        info = self.cr.fetchall()
        for row in info:
            rec = self.pool.get('sms.student').browse(self.cr ,self.uid ,row[0])
            
            my_dict = {'s_no':'','name':'','registration_no':'','gender':'','birthday':'','blood_grp':'','father_name':'',
                   'phone':'','email':'','cur_address':'','permanent_address':'','domocile':'','admitted_on':'','image':''}
            s_no +=1
            
            my_dict['s_no'] = s_no
            my_dict['name'] = rec.name 
            my_dict['registration_no'] = rec.registration_no 
            my_dict['gender'] = rec.gender 
            my_dict['birthday'] = rec.birthday 
            my_dict['blood_grp'] = rec.blood_grp
            my_dict['father_name'] = rec.father_name
            my_dict['phone'] = rec.phone
            my_dict['cell'] = rec.cell_no
            my_dict['fax'] = rec.fax_no
                
            my_dict['email'] = rec.email
            if rec.cur_city:
                current_city = rec.cur_city
            else:
                current_city = "--"
            if rec.cur_address:
                current_address = rec.cur_address
            else:
                current_address = "--"
            if rec.cur_country.name:
                current_country = rec.cur_country.name
            else:
                current_country = "--"
                
            my_dict['cur_address'] = str(current_address)+","+str(current_city)+","+str(current_country)
            
            if rec.permanent_city:
                permanent_city = rec.permanent_city
            else:
                permanent_city = "--"
            if rec.permanent_address:
                permanent_address = rec.permanent_address
            else:
                permanent_address = "--"
            if rec.cur_country.name:
                permanent_country = rec.permanent_country.name
            else:
                permanent_country = "--"
            
            my_dict['perm_address'] = str(permanent_address)+","+str(permanent_city)+","+str(permanent_country)
            
            if rec.permanent_city:
                perm_city = rec.permanent_city
            else:
                perm_city = '--'
            if rec.permanent_address:
                prem_address = rec.permanent_address
            else:
                prem_address = "--"
            if rec.permanent_country.name:
                prem_country = rec.permanent_country.name
            else:
                prem_country = "--"
                
            my_dict['permanent_address'] = str(prem_address)+","+str(perm_city)+","+str(prem_country)
            my_dict['domocile'] = rec.domocile
            my_dict['admitted_on'] = rec.admitted_on
            my_dict['image'] = rec.image
            res.append(my_dict)
        return res
        
    def print_student_se_passes(self,form):
            students = form['student_ids']
            result = []
    #         user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
    #         dummy_pic  = user.company_id.pic
    #        
            ids_entry_regis = self.pool.get('sms.student').search(self.cr,self.uid,[('state','=','Admitted'),('id','in',students)])
            if ids_entry_regis:
                rec_entryregis = self.pool.get('sms.student').browse(self.cr,self.uid,ids_entry_regis)
              
                i = 0
                  
                my_dict = {'id1': '','name1':'','father_name1':'','valid_upto1':'','pic1':'','dummy_pic1':'','program1':'','group1':'','candidate1':'',
                           'id2': '','name2':'','father_name2':'','valid_upto2':'','pic2':'','dummy_pic2':'','program2':'','group2':'','candidate2':''}
                if form['end_date']:
                    display_msg = form['card_display_message'] 
                else:
                    display_msg = ''
                for rec in rec_entryregis:
                    if rec.image:
                        picture = rec.image
                    else:
                        picture = 'No Picture'
                      
                    my_dict['id' + str((i%2)+1)] = i
                    my_dict['name' + str((i%2)+1)] = rec.name
                    my_dict['father_name' + str((i%2)+1)] = rec.father_name
                    my_dict['valid_upto' + str((i%2)+1)] = datetime.datetime.strptime(str(form['end_date']), '%Y-%m-%d').strftime('%d-%m-%Y')
                    my_dict['pic' + str((i%2)+1)] = picture
    #                 my_dict['dummy_pic' + str((i%2)+1)] = dummy_pic
                    my_dict['program' + str((i%2)+1)] = rec.current_class.name
                    my_dict['display_messge' + str((i%2)+1)] = display_msg
                    my_dict['candidate' + str((i%2)+1)] = rec.registration_no
                      
                    i = i + 1
                      
                    if i%2 == 0:
                        result.append(my_dict)
                        my_dict = {'id1': '','name1':'','father_name1':'','valid_upto1':'','pic1':'','dummy_pic1':'','program1':'','group1':'','candidate1':'',
                                  'id2': '','name2':'','father_name2':'','valid_upto2':'','pic2':'','dummy_pic2':'','program2':'','group2':'','candidate2':''}
                        
            if i%2 == 1:
                result.append(my_dict)
            return result

report_sxw.report_sxw('report.sms.studentslist.name', 'sms.student', 'addons/sms/rml_studentslist.rml',parser=sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.class.list.name', 'sms.student', 'addons/sms/rml_student_class_list.rml',parser=sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.std_admission_statistics.name', 'sms.student', 'addons/sms/rml_std_admission_statistics.rml',parser=sms_report_studentslist, header=False)
report_sxw.report_sxw('report.sms.students.biodata', 'sms.student', 'addons/sms/rml_studentsbiodata.rml',parser=sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms_students_securuty_cards_name', 'sms.student', 'addons/sms/report/rml_student_remp_sec_cards.rml',parser=sms_report_studentslist, header=False)
report_sxw.report_sxw('report.sms.withdrawn.student.details', 'sms.student', 'addons/sms/report/rml_withdrawnstudentsdata.rml',parser=sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.student.strength.report', 'sms.academiccalendar', 'addons/sms/report/rml_studentstrength.rml',parser=sms_report_studentslist, header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
