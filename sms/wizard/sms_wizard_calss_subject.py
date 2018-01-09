from openerp.osv import fields, osv
import datetime
from lxml.html.defs import form_tags

class sms_wizard_class_subject(osv.osv_memory):
    """Use this wizard to assign new subject to student"""
    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    
    def _get_current_subjects(self, cr, uid, ids):
        ftlist = []
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        print"dffdfdff",std_id
        sql="""SELECT current_class from sms_student 
        where id="""+str(std_id) + """ 
        AND current_state='Current'"""
        cr.execute(sql)
        stu_current_class = int(cr.fetchone()[0])
        sql = """SELECT id from sms_academiccalendar_student 
                 where std_id ="""+str(std_id) + """
                 AND name ="""+str(stu_current_class) + """
                  """
        cr.execute(sql)
        student_academicc_id = int(cr.fetchone()[0])
        
        
        sql = """SELECT subject from sms_student_subject 
                 where student_id ="""+str(std_id) + """
                 AND student ="""+str(student_academicc_id) + """ 
                 AND subject_status ='Current'
                            
                  """
        cr.execute(sql)
        ft_ids = cr.fetchall()
        
        print"aaaaaaaaaaaaaaaaaaa",ft_ids
        
        for ft in ft_ids:
            
            ftlist.append(ft[0])
#         print"cccccccccccccccc",ftlist
#         ftlist = tuple(ftlist)
#         ftlist = str(ftlist).rstrip(',)')
#         ftlist = ftlist+')'
        date='2017-01-01'
        student_id=6
        ids=[60]
        
        
        mname = self.pool.get('sms.collabrator').getstudent_personal_info( cr, uid, student_id)
          
        print"testtttttttttttttttttttttttt-----------------",mname
        return ftlist
  
    
    _name = "sms.wizard.class.subject"
    _description = "wizard for adding subject to student"                                
    _columns = {
         
         'student_cla_id': fields.many2one('sms.academiccalendar.student', 'Student Class ID', help="Select Student Class ID"),
         'student_id':fields.many2one('sms.student','StudentID'),
         'subject_ids':fields.many2many('sms.academiccalendar.subjects', 'sms_wizard_class_subject_rel', 'sms_wizard_class_subject_id', 'sms_academiccalendar_subjects_id', 'Subjects'),
         'state': fields.selection([('Current','Current'),('Pass','Pass'),('Withdraw','Withdraw'),('Fail','Fail'),('Suspended','Suspended')],'State', required = True),
             }
    
    _defaults = {
        'student_id':_get_student,
         'state':_get_current_subjects
                }

    def create_class_subject(self, cr, uid, ids, data):
       
        dat= self.read(cr, uid, ids)[0],
        form_data=dat[0]
        state=form_data["state"]
        student_id=form_data["student_id"][0]
        subject_ids=form_data["subject_ids"]
        
        if student_id:
           sql="""SELECT current_class from sms_student 
           where id="""+str(student_id) + """ 
           AND current_state='Current'"""
           cr.execute(sql)
           stu_current_class = int(cr.fetchone()[0])
        print"stu_current_class",stu_current_class
        if stu_current_class:
           sql = """SELECT id from sms_academiccalendar_student 
                 where std_id ="""+str(student_id) + """
                 AND name ="""+str(stu_current_class) + """
                  """
           cr.execute(sql)
           student_academicc_id = int(cr.fetchone()[0])
        print"subject_ids",subject_ids
        print"student_academicc_id",student_academicc_id
          
        if subject_ids:
            for subject_id in subject_ids:
                self.pool.get('sms.student.subject').create(cr,uid,{
                              
                                'student': student_academicc_id, 
                                'student_id':student_id,                                 
                                'subject':subject_id,
                                'subject_status':state })
        return
 
       
    
sms_wizard_class_subject()

