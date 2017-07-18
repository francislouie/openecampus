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
                        'address':obj[0].cur_address,
                        'city':obj[0].cur_city,
                        'login_status':1
                    }
        
            result.append(my_dict)
        return result
    
    def getstudent_subjects(self, cr, uid, student_id, aca_cal_id):
        result = []
        acad_cal_std_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=', aca_cal_id),('std_id','=', student_id),('subject_status','in',['Current','Promoted'])])
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
                    ORDER BY tab1.state desc""" 
                    
        cr.execute(sql)
        sql_recs = cr.fetchall()
        if sql_recs:
            for rec in sql_recs:
                if rec[7] == 'Monthly_Fee':
                    fee_name = rec[6] + " ("+ rec[5] +")"
                else:
                    fee_name = rec[6]
                     
                my_dict = {
                            'id':rec[0],
                            'fee_name':fee_name,
                            'date_fee_charged':rec[1],
                            'fee_amount':rec[3],
                            'paid_amount':rec[4],
                            'state':rec[2],
                            'return_status':1,
                            'return_desc':'Success'
                        }
                result.append(my_dict)
        else:
            my_dict = {
                        'return_status':0,
                        'return_desc':'No Fee Record Found'
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
    
sms_collabrator()
