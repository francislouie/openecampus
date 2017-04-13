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
        """ will be used by web profile method"""
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
    
    def getstudent_subjects(self, cr, uid, student_id):
        result = []
        student_subj_id = self.pool.get('sms.student.subject').search(cr,uid,[('student_id','=', student_id),('subject_status','=','Current')])
        if student_subj_id:
            for subject in self.pool.get('sms.student.subject').browse(cr, uid, student_subj_id):
                if subject.reference_practical_of:
                    practical = subject.reference_practical_of.name
                else:
                    practical = None
                my_dict = {
                            'subject_name':subject.subject.name,
                            'subject_status':subject.subject_status,
                            'subject_id':subject.id
                        }
                result.append(my_dict)
            
        return result
    
sms_collabrator()
