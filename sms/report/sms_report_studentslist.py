
import time
import datetime
from datetime import date

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
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        start_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['start_date'])
        end_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['end_date'])
               
        string = "Students Admissions \n " +str(start_date) + "-TO -"+str(end_date)
        return string
    
    def class_name(self, form): 
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,form['acad_cal'][0] ).name
    
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
  
  #############################################################################################################
  
    def print_students_class_list(self,form):                                                         
        result = []
        students = """SELECT registration_no,name,father_name,birthday,cell_no,phone
                          FROM sms_student WHERE current_class ="""+str(form['acad_cal'][0])+"""
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
    
    def get_admission_statistics(self, data):                                                         
        result = []
        this_form = self.datas['form']
        
        fee_st =tuple(self.pool.get('sms.feestructure').search(self.cr, self.uid,[]))
        acad_cal =tuple(self.pool.get('sms.academiccalendar').search(self.cr, self.uid,[('state', '!=','Closed')]))
        
        sql = """SELECT id FROM sms_academiccalendar
            WHERE ('""" + str(this_form['start_date']) + "' <=  date_started and '""" + this_form['end_date'] + """' >= date_started ) 
            OR ('""" + str(this_form['start_date']) + "' >=  date_started and '""" + this_form['end_date'] + """' <= date_closed ) 
            OR ('""" + str(this_form['start_date']) + "' <=  date_closed and '""" + this_form['end_date'] + """' >= date_closed ) 
            OR state = 'Draft'
            OR date_closed is null""" 
        
        self.cr.execute(sql)
        acad_cal = self.cr.fetchall()
       
        for cls in acad_cal:
            sub_list = []
            obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,cls[0])
            mydict = {'acad_cal':'','state':'','list':''}
            mydict['acad_cal'] = obj.name
            mydict['state'] = obj.state
            j = 1
            print "mydict['acad_cal']=",mydict['acad_cal']
            
            for fs in fee_st:
                inner_dict = {'SNO':'','fee_structure':'','no_admission':''}
                inner_dict['fee_structure'] = self.pool.get('sms.feestructure').browse(self.cr, self.uid,fs).name
                inner_dict['SNO'] = j
                
                
                sql = """SELECT count(sms_academiccalendar_student.id) FROM sms_student
                    inner join sms_academiccalendar_student on 
                    sms_student.id = sms_academiccalendar_student.std_id
                    WHERE sms_academiccalendar_student.name = """ + str(obj.id) + """ 
                    AND sms_student.fee_type = """ + str(fs) + """
                    AND sms_student.state in ('Admitted','admission_cancel','drop_out','slc') 
                    AND sms_student.admitted_on >= '""" + this_form['start_date'] + """'
                    AND sms_student.admitted_on <='""" + this_form['end_date'] + """'"""
                    
                
                self.cr.execute(sql)
                row = self.cr.fetchone()
                inner_dict['no_admission'] = row[0]
                if row[0] > 0:
                    sub_list.append(inner_dict)
                    j = j + 1

            mydict['list'] = sub_list
            if sub_list:
                result.append(mydict)
        return result
    
    def get_student_biodata(self,form):
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
            if not rec.phone:
                my_dict['phone'] = rec.cell_no
                
            my_dict['email'] = rec.email
            my_dict['cur_address'] = rec.cur_address
            my_dict['permanent_address'] = rec.permanent_address
            my_dict['domocile'] = rec.domocile
            my_dict['admitted_on'] = rec.admitted_on
            my_dict['image'] = rec.image
            res.append(my_dict)
            
        return res
    

      
report_sxw.report_sxw('report.sms.studentslist.name', 'sms.student', 'addons/sms/rml_studentslist.rml',parser = sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.class.list.name', 'sms.student', 'addons/sms/rml_student_class_list.rml',parser = sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.std_admission_statistics.name', 'sms.student', 'addons/sms/rml_std_admission_statistics.rml',parser = sms_report_studentslist, header='external')
report_sxw.report_sxw('report.sms.students.biodata', 'sms.student', 'addons/sms/rml_studentsbiodata.rml',parser = sms_report_studentslist, header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

