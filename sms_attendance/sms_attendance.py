from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
import xlwt
import xlrd
from dateutil import parser
from docutils.nodes import field_name

class sms_session(osv.osv):
    
    """ This object is add Attendance Features to Sessions"""

#     def create(self, cr, uid, vals, context=None, check=True):
#         year_id = super(sms_session, self).create(cr, uid, vals, context)
#         for f in self.browse(cr, uid, [year_id], context=context):
#             for class_obj in f.acad_cals:
#                 class_obj.attendace_punching = f.attendace_punching
#         return True
# 
#     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#         super(sms_session, self).write(cr, uid, ids, vals, context)
#         for f in self.browse(cr, uid, ids, context=context):
#             for class_obj in f.acad_cals:
#                 class_obj.attendace_punching = f.attendace_punching
#         return True

    def create(self, cr, uid, vals, context=None, check=True):
        year_id = super(sms_session, self).create(cr, uid, vals, context)
        return True

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(sms_session, self).write(cr, uid, ids, vals, context)
        if 'attendace_punching' in vals:
            for f in self.browse(cr, uid, ids):
                if 'attendace_punching' in vals:
                    for class_obj in f.acad_cals:
                        class_obj.attendace_punching = f.attendace_punching
        return True
        
    _name = 'sms.session'
    _inherit = 'sms.session'
    _columns = {
                'off_days':fields.one2many('sms.offdays', 'name', 'OFF Days'),
                'attendace_punching':fields.selection([('by_admin', 'Admin Staff'),
                                                     ('by_faculty', 'Faculty')], 'Attendance Punching', 
                                                      help='Describes the staff category who is going to punch attendance for this session'),
            } 
    _defaults = {
                 'attendace_punching': 'by_admin'
            }
sms_session()

class sms_offdays(osv.osv):

    _name = 'sms.offdays'
    _description = 'This objects holds off days for the school'
    _columns = {
                'name':fields.many2one('sms.session', 'Session Id'),
                'day_name':fields.selection([('Sunday', 'Sunday'),
                                             ('Friday', 'Friday'),
                                             ('Saturday', 'Saturday')], 'Day off', help='Off Day for School'),
                'remarks':fields.char('Remarks'),
            }
    _defaults = {}
sms_offdays()

class sms_academiccalendar(osv.osv):
 
    def _get_class_totalattendance(self, cr, uid, ids, name, args, context=None):
        """This method will return Total attendance for class"""
        res = {}
        for f in self.browse(cr, uid, ids, context):
            if f.class_id.id:
                
                sql = """SELECT count(id) from sms_class_attendance
                         where class_id =""" + str(f.id) +""""""
                cr.execute(sql)
                result = cr.fetchone()[0]
                res[f.id] = result
        return res
#     def get_class_attendance(self, cr, uid, ids, class_id, date):
#         sql = """SELECT 
#                 COALESCE(sum(CASE WHEN present THEN 1 ELSE 0 END),0) as present, 
#                 COALESCE(sum(CASE WHEN absent THEN 1 ELSE 0 END),0) as absent, 
#                 COALESCE(sum(CASE WHEN leave THEN 1 ELSE 0 END),0) as leave
#                 FROM sms_class_attendance_lines AS l, sms_class_attendance AS a
#                 where a.id = l.parent_id 
#                 and a.class_id = %s
#                 and a.attendance_date =  %s 
#                 """
# 
#         args = [class_id, date]
#         cr.execute(sql, args)
#         rec = cr.fetchone()
# 
#         result = {}
#         result.update({'present': rec[0]})
#         result.update({'absent': rec[1]})
#         result.update({'leave': rec[2]})
# 
#         return result
    def get_class_attendance(self, cr, uid, ids, class_id, date):
            sql = """SELECT 
                    COALESCE(sum(CASE WHEN present THEN 1 ELSE 0 END),0) as present, 
                    COALESCE(sum(CASE WHEN absent THEN 1 ELSE 0 END),0) as absent, 
                    COALESCE(sum(CASE WHEN leave THEN 1 ELSE 0 END),0) as leave
                    FROM sms_class_attendance_lines AS l, sms_class_attendance AS a,sms_academiccalendar_student AS std
                    where a.id = l.parent_id 
                    and l.student_class_id = std.id 
                    and std.state='Current'
                    and a.class_id = %s
                    and a.attendance_date =  %s 
                    """
    
            args = [class_id, date]
            cr.execute(sql, args)
            rec = cr.fetchone()
    
            result = {}
            result.update({'present': rec[0]})
            result.update({'absent': rec[1]})
            result.update({'leave': rec[2]})
    
            return result

    _name = 'sms.academiccalendar'
    _inherit = 'sms.academiccalendar'
    _columns = {
                'attendace_punching':fields.selection([('by_admin', 'Admin Staff'),
                                                     ('by_faculty', 'Faculty')], 'Attendance Punching', 
                                                    help='Describes the staff category who is going to punch attendance for this session'),
                
                 'get_class_totalattendance' : fields.function(_get_class_totalattendance, method=True, string='Class total attendance', type='integer',size=256),                   
            } 
    _defaults = {
                 'attendace_punching': 'by_admin'
            }
sms_academiccalendar()
class sms_academiccalendar_student(osv.osv):
 
    def _get_student_attendance(self, cr, uid, ids,field_name, args, context=None):
        """This method will return Total attendance for class"""
        result = {}
        state=""
        for f in self.browse(cr, uid, ids, context):
            result[f.id] = {} 
            if type(field_name)is not list:
                field_name = [field_name]
            for key_str in field_name:
                result[f.id][key_str] = 0
                if 'total_present'in field_name:
                    state ='Present'
                if 'total_absent'in field_name:
                    state ='Absent'
                if 'total_leave'in field_name:
                    state ='Leave' 
                if 'attendace_percentage'in field_name:    
                    sql = """SELECT count(id) from sms_class_attendance
                         where class_id =""" + str(f.name.id) +""""""
                    cr.execute(sql) 
                    total_rec = cr.fetchone()[0]
                    print"total classes",total_rec
                    
                    sql = """SELECT count(sms_class_attendance.id) from sms_class_attendance inner join  sms_class_attendance_lines on sms_class_attendance.id=sms_class_attendance_lines.parent_id
                          where sms_class_attendance.class_id =""" + str(f.name.id) + """
                          AND   sms_class_attendance_lines.student_name=""" + str(f.std_id.id) + """
                          AND   sms_class_attendance_lines.state='Present'"""
                    cr.execute(sql)
                    Present_rec = cr.fetchone()[0]
                    
                    res = float(Present_rec) / float(total_rec)*100
                    
                    result[f.id] = res
                    return result
                if 'not_taken'in field_name:
                    
                    sql = """SELECT count(id) from sms_class_attendance
                         where class_id =""" + str(f.name.id) +""""""
                    cr.execute(sql)
                    total_classes=cr.fetchone()[0]
                    sql = """SELECT count(sms_class_attendance.id) from sms_class_attendance inner join  sms_class_attendance_lines on sms_class_attendance.id=sms_class_attendance_lines.parent_id
                              where sms_class_attendance.class_id =""" + str(f.name.id) + """
                              AND   sms_class_attendance_lines.student_name=""" + str(f.std_id.id) + """
                              """
                    cr.execute(sql)
                    resul = cr.fetchone()[0]
                    result[f.id] =total_classes - resul
                    return result
                sql = """SELECT count(sms_class_attendance.id) from sms_class_attendance inner join  sms_class_attendance_lines on sms_class_attendance.id=sms_class_attendance_lines.parent_id
                          where sms_class_attendance.class_id =""" + str(f.name.id) + """
                          AND   sms_class_attendance_lines.student_name=""" + str(f.std_id.id) + """
                          AND   sms_class_attendance_lines.state='""" + str(state) + """'
                          """
    
                cr.execute(sql)
                resul = cr.fetchone()[0]
                print"result",resul
                result[f.id] = resul
        return result
    
    
    def _get_student_att_per(self, cr, uid, ids,field_name, args, context=None):
        """This method will return Total attendance for class"""
        res = {}
        if 'attendace_percentage'in field_name:
            for f in self.browse(cr, uid, ids, context):
                if f.name:
                     
                    sql = """SELECT count(id) from sms_class_attendance
                         where class_id =""" + str(f.name.id) +""""""
                    cr.execute(sql) 
                    rec = cr.fetchone()[0]
                    print"Total class atte",rec
                    
                         
                    sql = """SELECT count(sms_class_attendance.id) from sms_class_attendance inner join  sms_class_attendance_lines on sms_class_attendance.id=sms_class_attendance_lines.parent_id
                              where sms_class_attendance.class_id =""" + str(f.name.id) + """
                              AND   sms_class_attendance_lines.student_name=""" + str(f.std_id.id) + """
                              ANd   sms_class_attendance_lines.state = 'Present'  
                              """
    
                    cr.execute(sql)
                    present_rec = cr.fetchone()[0]
                    
                    
                    
                    print"present class atte",present_rec
                    result = float(present_rec) / float(rec)*100
                    print"result",result
                    res[f.id] = result
        return res
 
    _name = 'sms.academiccalendar.student'
    _inherit = 'sms.academiccalendar.student'
    _columns = {
        
                 'total_present' : fields.function(_get_student_attendance, method=True, string='Present', type='integer',size=256),                   
                 
                 'total_absent' : fields.function(_get_student_attendance, method=True, string='Absent', type='integer',size=256),                   
                
                 'total_leave' : fields.function(_get_student_attendance, method=True, string='leave', type='integer',size=256), 
                 'attendace_percentage' : fields.function(_get_student_attendance, method=True, string='percentage', type='integer',size=256),  
                 'not_taken' : fields.function(_get_student_attendance, method=True, string='Not Taken', type='integer',size=256),                                                
            } 
    _defaults = {
            }
sms_academiccalendar_student()
####
class sms_student(osv.osv):
    
    def get_attendance_on_period_selection(self, cr, uid, ids, student_id, date_from, date_to):
            print"get_attendance_on_date_list method is called from sms"
            sql = """SELECT 
                    COALESCE(sum(CASE WHEN present THEN 1 ELSE 0 END),0) as present, 
                    COALESCE(sum(CASE WHEN absent THEN 1 ELSE 0 END),0) as absent, 
                    COALESCE(sum(CASE WHEN leave THEN 1 ELSE 0 END),0) as leave
                    FROM sms_class_attendance_lines AS l, sms_class_attendance AS a,sms_academiccalendar_student AS std
                    where a.id = l.parent_id 
                    and l.student_class_id = std.id
                    and std.state='Current'
                    and l.student_name = %s 
                    and a.attendance_date >=  %s 
                    and a.attendance_date <=  %s 
                    """
    
            args = [student_id, date_from, date_to]
            cr.execute(sql, args)
            rec = cr.fetchone()
    
            result = {}
            result.update({'present': rec[0]})
            result.update({'absent': rec[1]})
            result.update({'leave': rec[2]})
    
            return result
        
        
    _name = 'sms.student'
    _inherit = 'sms.student'
    _columns = {
                'attendance_status_ids' : fields.one2many('sms.class.attendance.lines','student_name','Student Attendance'),
            } 
sms_student()
###


class sms_class_attendance(osv.osv):

    def create(self, cr, uid, vals, context=None, check=True):
        record = super(osv.osv, self).create(cr, uid, vals, context)
        for rec in self.browse(cr, uid, [record], context=context):
            current_day = datetime.datetime.strptime(str(rec.attendance_date), '%Y-%m-%d').strftime('%A') 
            for child_rec in rec.class_id.session_id.off_days:
                #---------------------------------------------------------
                if not child_rec.day_name:
                    offday = 'Sunday'
                else:
                    offday = child_rec.day_name
                #---------------------------------------------------------
                if current_day == offday:
                    raise osv.except_osv(('Permission Denied!'), ('Cannot punch date on Off Days'))
                else:
                    continue
            return record
        
    def cancel_attendance(self, cr, uid, ids, context):
        rec = self.browse(cr ,uid ,ids)[0]
        for attendance_lines in rec.child_id:
            self.pool.get('sms.class.attendance.lines').unlink(cr ,uid ,attendance_lines.id ,context) 
        self.write(cr ,uid ,ids ,{'state':'Draft'})
        return None
    
    def mark_attendance(self, cr, uid, ids, context):
        rec = self.browse(cr ,uid ,ids)[0]
        for acd_cal in rec.class_id.acad_cal_students:
            per= self.pool.get('sms.academiccalendar.student').browse(cr ,uid ,acd_cal.id)
            self.pool.get('sms.class.attendance.lines').create(cr ,uid ,{'parent_id': rec.id ,
                                                                        'student_name':acd_cal.std_id.id  ,
                                                                        'student_class_id':acd_cal.id  ,
                                                                        'registration_no':acd_cal.std_id.registration_no,    
                                                                        'std_agr_att_on_date':per.attendace_percentage
                                                                        })
        self.write(cr ,uid ,ids ,{'state':'waiting_approval' ,'class_teacher':rec.class_id.class_teacher.id })
        return True

    def edit_attendance(self ,cr ,uid ,ids ,context):
        self.write(cr ,uid ,ids ,{'state':'waiting_approval' , 'punched_by':uid})
        return True
        
    def submit_attendance(self ,cr ,uid ,ids ,context):
        rec = self.browse(cr ,uid ,ids)[0]
        for a_lines in rec.child_id:
            if a_lines.present == False and a_lines.absent == False and a_lines.leave == False:
                self.pool.get('sms.class.attendance.lines').write(cr ,uid ,a_lines.id ,{'state':'Present' ,'present':True })
            elif a_lines.present == True and a_lines.absent == False and a_lines.leave == False:
                self.pool.get('sms.class.attendance.lines').write(cr ,uid ,a_lines.id ,{'state':'Present'})
        self.write(cr ,uid ,ids ,{'state':'Submit' , 'punched_by':uid})
        return None
#      return {'domain': {'group':[('id','=',acad_cal_obj.group_id.id ) ]},'value': vals}
    def onchange_set_domain(self, cr, uid , ids, class_id, attendance_date, context=None):
        result = {}
        user_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        if not len(user_ids):
            raise osv.except_osv(('Error!'), ('Please create an employee and associate it with this user.'))
        cr.execute("""select id,job_id  from hr_employee where resource_id =(select id from resource_resource where user_id =""" + str(uid) + """  )""")
        emp_obj = cr.fetchone()
        teacher_id = emp_obj[0]
        tea_job_id = emp_obj[1]
        if class_id:
            rec = self.pool.get('sms.academiccalendar').browse(cr ,uid ,[class_id])[0]
            if attendance_date < rec.session_id.start_date or attendance_date > rec.session_id.end_date:
                raise osv.except_osv(('Invalid Date'), ('Your date should be within session i.e from   '+str(rec.session_id.start_date)+' to '+str(rec.session_id.end_date) ))
            result['class_teacher'] = rec.class_teacher.id
        else:
            result['class_teacher'] = None
#         if tea_job_id ==1:   
#             return {'domain': {'class_id':[('class_teacher','=',teacher_id) ]},'value': result}
#         else:
            return {'domain': {'class_id':[('state','=','Active') ]},'value': result}
    
    def _user_get(self,cr,uid,context={}):
        return uid

    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            attendance_date = f.attendance_date
            attendance_date = datetime.datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%m/%d/%Y')
            result[f.id] = str(f.class_id.name) + " - " + str(attendance_date)
        return result
    
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    _name = 'sms.class.attendance'
    _columns = {
        'name' : fields.function(_set_name, method=True, store=True, size=256, string='Name', type='char'),
        'class_id' : fields.many2one('sms.academiccalendar',' Class', required=True),
        'class_teacher' : fields.many2one('hr.employee', 'Class Teacher'),
        'attendance_date' :fields.date('Date', required=True),
        'punched_by' : fields.many2one('res.users','  Punched By'),
        'child_id' : fields.one2many('sms.class.attendance.lines','parent_id','Student Attendance'),
        'state' : fields.selection([('Draft','Draft'),('waiting_approval','Waiting Approval'),('Submit','Submit')],'Status'),
    }
    _defaults = {'state': 'Draft',
                 'punched_by':_user_get,
                 'attendance_date':lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
                 }  
    _sql_constraints = [('class_date', 'unique(attendance_date,class_id)', 'Attendance for the selected class has already been punched.')]
sms_class_attendance()

class sms_class_attendance_lines(osv.osv):

    def onchange_set_absent(self,cr ,uid ,ids ,absent ,context=None):
        result = {}
        if absent==True:
            result['present'] = False 
            result['leave'] = False
            self.write(cr , uid, ids, {'state':'Absent',
                                       'absent':False,
                                       'leave':False })
        return {'value': result}
    
    def onchange_set_leave(self,cr ,uid ,ids ,leave ,context=None):
        result = {}
        if leave == True :
            result['absent'] = False 
            result['present'] = False
            self.write(cr , uid, ids, {'state':'Leave',
                                       'absent':False,
                                       'leave':False})
        
        return {'value': result}
    
    def onchange_set_present(self,cr ,uid ,ids ,present ,context=None):
        result = {}
        if present == True :
            result['absent'] = False 
            result['leave'] = False
            self.write(cr , uid, ids,{'state':'Present',
                                      'absent':False,
                                      'leave':False })
        return {'value': result}
        
#     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):                
#         raise osv.except_osv(('Not Allowed'), ('S..................s.'))
#         return
    def get_class_date(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            attendance_date = f.parent_id.attendance_date
            
            print "attendance date level 1",attendance_date
            if f.parent_id.id:
                attendance_date = datetime.datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%d-%m-%Y')
            result[f.id] = str(attendance_date)
        return result
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    _name = 'sms.class.attendance.lines'
    _columns = {
        'parent_id' : fields.many2one('sms.class.attendance','Class Attendance'),
     #   'student_name' : fields.char('Student',size=256),
        'student_name' : fields.many2one('sms.student','Student', required=True),
        'student_class_id' : fields.many2one('sms.academiccalendar.student','Student Class'),
        'present' :fields.boolean('Present'),
        'absent' :fields.boolean('Absent'),
        'leave' :fields.boolean('Leave'),
        'state' : fields.selection([('Draft','Draft'),('Present','Present'),('Absent','Absent'),('Leave','Leave')],'Status'),
        'std_agr_att_on_date' :fields.float('Per on given date'),
        'registration_no': fields.char(string = "Registration No.", size=32),
        'class_date' : fields.function(get_class_date, method=True, string='Class Date', type='char',size=50),#jsut for display purpose
    }
    _defaults = {'state': 'Present' , 'present': True}    
    
sms_class_attendance_lines()

