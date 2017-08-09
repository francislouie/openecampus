from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
import xlwt
import xlrd
from dateutil import parser

class sms_session(osv.osv):
    
    """ This object is add Attendance Features to Sessions"""

    def create(self, cr, uid, vals, context=None, check=True):
        year_id = super(sms_session, self).create(cr, uid, vals, context)
        for f in self.browse(cr, uid, [year_id], context=context):
            print "it works"
        return True

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if 'attendace_punching' in vals:
            for f in self.browse(cr, uid, ids):
                if 'attendace_punching' in vals:
                    for class_obj in f.acad_cals:
                        class_obj.attendace_punching = f.attendace_punching
            super(sms_session, self).write(cr, uid, ids, vals, context)
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
    
    _name = 'sms.academiccalendar'
    _inherit = 'sms.academiccalendar'
    _columns = {
                'attendace_punching':fields.selection([('by_admin', 'Admin Staff'),
                                                     ('by_faculty', 'Faculty')], 'Attendance Punching', 
                                                      help='Describes the staff category who is going to punch attendance for this session'),
            } 
    _defaults = {
                 'attendace_punching': 'by_admin'
            }
sms_academiccalendar()

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
            self.pool.get('sms.class.attendance.lines').create(cr ,uid ,{'parent_id': rec.id ,
                                                                        'student_name':acd_cal.std_id.id  ,
                                                                        'student_class_id':acd_cal.id  ,
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
    
    def onchange_set_domain(self, cr, uid , ids, class_id, attendance_date, context=None):
        result = {}
        if class_id:
            rec = self.pool.get('sms.academiccalendar').browse(cr ,uid ,[class_id])[0]
            if attendance_date < rec.session_id.start_date or attendance_date > rec.session_id.end_date:
                raise osv.except_osv(('Invalid Date'), ('Your date should be within session i.e from   '+str(rec.session_id.start_date)+' to '+str(rec.session_id.end_date) ))
            result['class_teacher'] = rec.class_teacher.id
        else:
            result['class_teacher'] = None
        return {'value': result}
    
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
        'class_id' : fields.many2one('sms.academiccalendar',' Class' ,required=True),
        'class_teacher' : fields.many2one('res.users',' Teacher Name' ),
        'attendance_date' :fields.date('Date' ,required=True),
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
    
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    _name = 'sms.class.attendance.lines'
    _columns = {
        'parent_id' : fields.many2one('sms.class.attendance','Class Attendance'),
     #   'student_name' : fields.char('Student',size=256),
        'student_name' : fields.many2one('sms.student','Student'),
        'student_class_id' : fields.many2one('sms.academiccalendar.student','Student Class'),
        'present' :fields.boolean('present'),
        'absent' :fields.boolean('absent'),
        'leave' :fields.boolean('leave'),
        'state' : fields.selection([('Draft','Draft'),('Present','Present'),('Absent','Absent'),('Leave','Leave')],'Status'),
    }
    _defaults = {'state': 'Present' , 'present': True}    
    
sms_class_attendance_lines()

