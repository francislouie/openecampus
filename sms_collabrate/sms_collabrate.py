from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import xlwt
import xlrd
from datetime import datetime, timedelta
from datetime import datetime
from dateutil import parser
import logging
import datetime

class sms_collabrator(osv.osv):
    
    """ Servers as bridge among sms and external apps """
    _name = 'sms.collabrator'
    _columns = {}
           
    def mast_auth(self, cr, uid, login, pwd):
        result = []
        student_id = self.pool.get('sms.student').search(cr,uid,[('login_id','=',login),('password','=',pwd), ('state','=','Admitted')])
        if student_id:
            obj = self.pool.get('sms.student').browse(cr, uid, student_id)
            my_dict = {
                        'registration_no':obj[0].registration_no,
                        'stdname':obj[0].name,
                        'fathername':obj[0].father_name,
                        'class_id':obj[0].current_class.id,
                        'class_name':obj[0].current_class.name,
                        'pic':obj[0].image,
                        'std_id':obj[0].id,
                        'transport_availed':obj[0].transport_availed,
                        'state':obj[0].state,
                        'login_status':1
                    }
            result.append(my_dict)
        else:
            my_dict = {
                        'state':'Invalid Credentials',
                        'login_status':0
                    }
            result.append(my_dict)
        return result
    
    def getstudent_personal_info(self, cr, uid, student_id):
        """ will be used by web profile method in any case this method will return a response, 0 mean unsucess read or browse"""
        result = []
        student_id = self.pool.get('sms.student').search(cr,uid,[('id','=', student_id), ('state','=','Admitted')])
        if student_id:
            obj = self.pool.get('sms.student').browse(cr, uid, student_id)
            my_dict = {
                        'registration_no':obj[0].registration_no,
                        'stdname':obj[0].name,
                        'fathername':obj[0].father_name,
                        'class_id':obj[0].current_class.id,
                        'class_name':obj[0].current_class.name,
                        'pic':obj[0].image,
                        'std_id':obj[0].id,
                        'state':obj[0].state,
                        'blood_group':obj[0].blood_grp,
                        'gender':obj[0].gender,
                        'date_of_birth':obj[0].birthday,
                        'father_nic':obj[0].father_nic,
                        'contact_no_1':obj[0].phone,
                        'contact_no_2':obj[0].cell_no,
                        'email':obj[0].email,
                        'transport_availed':obj[0].transport_availed,
                        'address':obj[0].cur_address,
                        'city':obj[0].cur_city,
                        'display_contact_info':obj[0].display_contacts_portal,
                        'login_status':1
                    }
            result.append(my_dict)
        return result

    def getstudent_notifications(self, cr, uid, student_id):
        result = []
        sql = """
                SELECT id, name ,state, body 
                FROM sms_mass 
                WHERE student_id = """+str(student_id)+""" 
                ORDER BY id""" 
        cr.execute(sql)
        sql_recs = cr.fetchall()
        if sql_recs:
            for rec in sql_recs:
                if not rec[1]:
                    name = 'Null'
                else:
                    name = rec[1]
                if not rec[3]:
                    body = 'Empty'
                else:
                    body = rec[3]
                my_dict = {
                            'id':rec[0],
                            'name':name,
                            'state':rec[2],
                            'body':body,
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                                'return_status':0,
                                'return_desc':'No Active Class Found'
                            }
            result.append(my_dict)
        return result
    
    def getstudent_subjects(self, cr, uid, student_id, aca_cal_id):
        result = []
        acad_cal_std_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=', aca_cal_id),('std_id','=', student_id),('state','in',['Current','Promoted'])])
        if acad_cal_std_id:
            student_subj_id = self.pool.get('sms.student.subject').search(cr,uid,[('student','=', acad_cal_std_id),('subject_status','in',['Current','Pass'])])
            if student_subj_id:
                for subject in self.pool.get('sms.student.subject').browse(cr, uid, student_subj_id):
                    
                    my_dict = {
                                'subject_name':subject.subject.name,
                                'subject_status':subject.subject_status,
                                'subject_id':subject.id,
                                'return_status':1,
                                'return_desc':'Success'
                            }
                    result.append(my_dict)
            else:
                my_dict = {
                                'return_status':0,
                                'return_desc':'No Subjects Found'
                            }
                result.append(my_dict)
        else:
            my_dict = {
                                'return_status':0,
                                'return_desc':'No Active Class Found'
                            }
            result.append(my_dict)
        return result
    
    def stdfee_history(self, cr, uid, student_id, aca_cal_id, category):
        result = []
        get_portal_setting = """SELECT fee_display_portal from res_company"""
        cr.execute(get_portal_setting)
        sql_rec_ = cr.fetchone()
        
        if category == 'Academics':
            sql = """
                    SELECT tab1.id, tab1.date_fee_charged, tab1.state, tab1.fee_amount, 
                    tab1.paid_amount, tab4.name, tab3.name, tab3.subtype
                    FROM smsfee_studentfee as tab1
                    INNER JOIN smsfee_classes_fees_lines as tab2
                    ON tab1.fee_type = tab2.id
                    INNER JOIN smsfee_feetypes as tab3
                    ON tab2.fee_type = tab3.id
                    INNER JOIN sms_session_months as tab4
                    ON tab1.fee_month = tab4.id
                    WHERE tab1.student_id ="""+str(student_id)+""" 
                    AND tab1.acad_cal_id ="""+str(aca_cal_id)+""" 
                    AND tab3.category = 'Academics'
                    AND tab1.state= '"""+str(sql_rec_[0])+"""'
                    ORDER BY tab1.state desc"""
                    
        elif category == 'Transport':
            sql = """
                    SELECT tab1.id, tab1.date_fee_charged, tab1.state, tab1.fee_amount, 
                    tab1.paid_amount, tab4.name, tab3.name, tab3.subtype
                    FROM smsfee_studentfee as tab1
                    INNER JOIN smsfee_classes_fees_lines as tab2
                    ON tab1.fee_type = tab2.id
                    INNER JOIN smsfee_feetypes as tab3
                    ON tab2.fee_type = tab3.id
                    INNER JOIN sms_session_months as tab4
                    ON tab1.fee_month = tab4.id
                    WHERE tab1.student_id ="""+str(student_id)+""" 
                    AND tab1.acad_cal_id ="""+str(aca_cal_id)+""" 
                    AND tab3.category = 'Transport'
                    AND tab1.state= '"""+str(sql_rec_[0])+"""'
                    ORDER BY tab1.state desc"""
                    
        else:
            sql = """
                    SELECT tab1.id, tab1.date_fee_charged, tab1.state, tab1.fee_amount, 
                    tab1.paid_amount, tab4.name, tab3.name, tab3.subtype
                    FROM smsfee_studentfee as tab1
                    INNER JOIN smsfee_classes_fees_lines as tab2
                    ON tab1.fee_type = tab2.id
                    INNER JOIN smsfee_feetypes as tab3
                    ON tab2.fee_type = tab3.id
                    INNER JOIN sms_session_months as tab4
                    ON tab1.fee_month = tab4.id
                    WHERE tab1.student_id ="""+str(student_id)+""" 
                    AND tab1.acad_cal_id ="""+str(aca_cal_id)+"""
                    AND tab1.state= '"""+str(sql_rec_[0])+"""'
                    ORDER BY tab1.state desc""" 

        cr.execute(sql)
        sql_recs = cr.fetchall()
        
        if sql_recs:
            for rec in sql_recs:
                if rec[7] == 'Monthly_Fee':
                    fee_name = rec[6] + " ("+ rec[5] +")"
                else:
                    fee_name = rec[6]
                if not rec[4]:
                    paid_amount = 0
                else:
                    paid_amount = rec[4]
                if not rec[3]:
                    fee_amount = 0
                else:
                    fee_amount = rec[3]
                if not rec[1]:
                    date_fee_charged = '1960-01-01'
                else:
                    date_fee_charged = rec[1]
                    
                my_dict = {
                            'id':rec[0],
                            'fee_name':fee_name,
                            'date_fee_charged':date_fee_charged,
                            'fee_amount':fee_amount,
                            'paid_amount':paid_amount,
                            'state':rec[2],
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Record Found'
                        }
            result.append(my_dict)
        return result

    def stdfee_refundable(self, cr, uid, student_id):
        result = []
        get_portal_setting = """SELECT display_refundable from res_company"""
        cr.execute(get_portal_setting)
        sql_rec_ = cr.fetchone()
        if sql_rec_[0] == True:
            sql = """
                    SELECT tab1.id, tab1.amount_received, tab1.amount_paid_back, 
                    tab1.state, tab1.receipt_no, tab2.category 
                    FROM smsfee_studentfee_refundable AS tab1 
                    INNER JOIN smsfee_studentfee AS tab2
                    ON tab1.student_fee_id = tab2.id
                    WHERE tab1.student_id = """+str(student_id)+""" 
                    ORDER BY tab1.id""" 
            
            cr.execute(sql)
            sql_recs = cr.fetchall()
            if sql_recs:
                for rec in sql_recs:
                    if rec[2] == 'to_be_paid':
                        state = 'To be Paid Back' 
                    elif rec[2] == 'paid_back':
                        state = 'Paid To Student'
                    else:
                        state = 'Adjusted'
                    if not rec[1]:
                        amt_received = 0
                    else:
                        amt_received = rec[1]
                    if not rec[2]:
                        amt_paid = 0
                    else:
                        amt_paid = rec[2]
                    if not rec[4]:
                        receipt_no = 'Null'
                    else:
                        receipt_no = rec[4]
                    if not rec[5]:
                        fee_cat = 'Not Defined'
                    else:
                        fee_cat = rec[5]
                    my_dict = {
                                'id':rec[0],
                                'amount_received':amt_received,
                                'state':state,
                                'amount_paid_back':amt_paid,
                                'receipt_no':receipt_no,
                                'fee_category':fee_cat,
                                'return_status':1,
                                'return_desc':'Success'
                            }
                    result.append(my_dict)
            else:
                my_dict = {
                            'return_status':0,
                            'return_desc':'No Record Found'
                            }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'Fee Refundables Cannot Be Displayed Please Contact Office'
                        }
            result.append(my_dict)
        return result

    def stdfee_feebils(self, cr, uid, student_id, state, category):
        result = []
        receipt_ids = self.pool.get('smsfee.receiptbook').search(cr,uid, [('student_id','=', student_id),
                                                                          ('state','=',state),
                                                                          ('challan_cat','=',category)])
        if receipt_ids:
            for this_recipt in self.pool.get('smsfee.receiptbook').browse(cr, uid, receipt_ids):
                if this_recipt.manual_recpt_no:
                    receipt_no = this_recipt.manual_recpt_no
                else:
                    receipt_no = 'Null'
                    
                my_dict = {
                            'id':this_recipt.id,
                            'name':this_recipt.name,
                            'receipt_date':this_recipt.receipt_date,
                            'manual_receipt_no':receipt_no,
                            'total_paybles':this_recipt.total_paybles,
                            'total_paid_amount':this_recipt.total_paid_amount,
                            'due_date':'2017-01-01',
                            'challan_cat':this_recipt.challan_cat,
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Record Found'
                        }
            result.append(my_dict)
        return result

    def sms_weekly_calendar(self, cr, uid, state):
        result = []
        sql = """
                SELECT id, name, state, start_date, end_date 
                FROM sms_calander_week 
                WHERE state = '"""+str(state)+"""' 
                ORDER BY id""" 
                
        cr.execute(sql)
        sql_recs = cr.fetchall()
        if sql_recs:
            for rec in sql_recs:
                my_dict = {'id':rec[0],
                        'week_no':rec[1],
                        'state':rec[2],
                        'start_date':rec[3],
                        'end_date':rec[4],
                        'return_status':1,
                        'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Record Found'
                        }
            result.append(my_dict)
        return result
    
    def sms_weekly_plan(self, cr, uid, week_id):
        result = []
        sql = """
                SELECT sms_weekly_plan.id, sms_weekly_plan.teacher, sms_weekly_plan.work_guide,
                sms_subject.name
                FROM sms_weekly_plan 
                INNER JOIN sms_academiccalendar_subjects ON
                sms_weekly_plan.subject = sms_academiccalendar_subjects.id
                INNER JOIN sms_subject ON 
                sms_academiccalendar_subjects.subject_id = sms_subject.id
                WHERE sms_weekly_plan.week = """+str(week_id)+""" 
                ORDER BY id""" 

        cr.execute(sql)
        sql_recs = cr.fetchall()
        if sql_recs:
            for rec in sql_recs:
                my_dict = {'id':rec[0],
                            'subject':rec[3],
                            'work_plan':rec[2],
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Record Found'
                        }
            result.append(my_dict)
        return result

    def sms_exam_datesheet(self, cr, uid, class_id):
        result = []
        sql = """SELECT tab1.id, tab1.name, tab1.start_date, tab1.status, 
                tab2.subject, tab4.name, tab2.invigilator, tab5.name_related, tab2.paper_date
                FROM sms_exam_datesheet AS tab1
                INNER JOIN sms_exam_datesheet_lines AS tab2
                ON tab1.id = tab2.name
                INNER JOIN sms_academiccalendar_subjects AS tab3
                ON tab2.subject = tab3.id 
                INNER JOIN sms_subject AS tab4
                ON tab3.subject_id = tab4.id 
                INNER JOIN hr_employee AS tab5
                ON tab2.invigilator = tab5.id 
                WHERE tab1.academiccalendar = """+str(class_id)+"""
                AND tab1.status = 'Active'
                ORDER BY tab2.subject""" 
                
        cr.execute(sql)
        sql_recs = cr.fetchall()
        if sql_recs:
            for rec in sql_recs:
                my_dict = {'id':rec[0],
                            'exam_name':rec[1],
                            'exam_start_date':rec[2],
                            'exam_state':rec[3],
                            'subject_id':rec[4],
                            'subject_name':rec[5],
                            'invigilator_id':rec[6],
                            'invigilator_name':rec[7],
                            'paper_date':rec[8],
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Record Found'
                        }
            result.append(my_dict)
        return result  

    def sms_exam_marksheet(self, cr, uid, student_id, class_id):
        result = []
        get_portal_setting = """SELECT hide_exammarks_portal FROM sms_student WHERE id= """+str(student_id)
        cr.execute(get_portal_setting)
        sql_rec_ = cr.fetchone()
        if sql_rec_[0] == False or sql_rec_[0] == None:
            sql = """SELECT tab1.id, tab6.name, tab1.exam_status,  tab2.student_id, 
                    tab2.subject, tab5.name, tab1.obtained_marks, tab1.total_marks
                    FROM sms_exam_lines AS tab1
                    INNER JOIN sms_student_subject AS tab2
                    on tab1.student_subject = tab2.id
                    INNER JOIN sms_academiccalendar_student AS tab3
                    on tab2.student_id = tab3.std_id
                    INNER JOIN sms_academiccalendar_subjects AS tab4
                    on tab2.subject = tab4.id
                    INNER JOIN sms_subject AS tab5
                    on tab4.subject_id = tab5.id
                    INNER JOIN sms_exam_datesheet AS tab6
                    ON tab1.name = tab6.id
                    WHERE tab2.student_id = """+str(student_id)+"""
                    AND tab2.subject IN (SELECT DISTINCT tab2.subject 
                    FROM sms_exam_datesheet AS tab1
                    INNER JOIN sms_exam_datesheet_lines AS tab2
                    ON tab1.id = tab2.name
                    INNER JOIN sms_academiccalendar_subjects AS tab3
                    ON tab2.subject = tab3.id 
                    WHERE tab1.academiccalendar = """+str(class_id)+"""
                    AND tab1.status = 'Active'
                    ORDER BY tab2.subject)
                    ORDER BY tab2.student_id""" 
                    
            cr.execute(sql)
            sql_recs = cr.fetchall()
            if sql_recs:
                for rec in sql_recs:
                    my_dict = {'id':rec[0],
                                'exam_name':rec[1],
                                'student_attendance':rec[2],
                                'student_id':rec[3],
                                'subject_id':rec[4],
                                'subject_name':rec[5],
                                'obtained_marks':rec[6],
                                'total_marks':rec[7],
                                'return_status':1,
                                'return_desc':'Success'
                            }
                    result.append(my_dict)
            else:
                my_dict = {
                            'return_status':0,
                            'return_desc':'No Record Found'
                            }
                result.append(my_dict)
        else:
            my_dict = {
                    'return_status':0,
                    'return_desc':'Record Not found due to missing exams or defaulter list'
                    }
            result.append(my_dict)
        return result  
    
sms_collabrator()
