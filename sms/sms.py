from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
import xlwt
import xlrd
from dateutil import parser

class res_company(osv.osv):
    """This object is used to add fields in company.fields are extended."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
    'signature_principal': fields.binary('Principal Signature'), 
    'declaration_student_admission': fields.text('Admission Declaration'),
    'slc_text': fields.text('Certificate Text'),
    'character_certificate_text': fields.text('Character Certificate Text'),
    'provisional_certificate_text': fields.text('Provisional Certificate Text'),
    'sports_certificate_text': fields.text('Sports Certificate Text'),
    'default_gender':fields.selection([('Male','Male'),('Female','Female')],'Defaulter Gender',required = True),
    'default_dmc_format':fields.selection([('format1','Format 1'),('format2','Format 2')],'DMC Format',required = True)
    }
    
    _defaults = {
    }
res_company()


class sms_academics_session(osv.osv):
    """
    This Creates an academic session thame may be of minimum 1 year, max many years
    """
    
    def close_academic_session(self, cr, uid, ids, *args):
   
        result = {}
        for f in self.browse(cr, uid, ids):
            a_session = self.write(cr, uid, f.id, {'state': 'Closed','date_closed': datetime.date.today(),'closed_by':uid})
            return
    
    def start_new_academic_session(self, cr, uid, ids, *args):
   
        result = {} 
        for f in self.browse(cr, uid, ids):
            state = ''
            start_date = f.start_date
            end_date = f.end_date
            
            
            
            s_year = int(datetime.datetime.strptime(str(f.start_date), '%Y-%m-%d').strftime('%Y'))
            s_month = int(datetime.datetime.strptime(str(f.start_date), '%Y-%m-%d').strftime('%m'))
            s_day = int(datetime.datetime.strptime(str(f.start_date), '%Y-%m-%d').strftime('%d'))
            
            e_year = int(datetime.datetime.strptime(str(f.end_date), '%Y-%m-%d').strftime('%Y'))
            e_month = int(datetime.datetime.strptime(str(f.end_date), '%Y-%m-%d').strftime('%m'))
            e_day = int(datetime.datetime.strptime(str(f.end_date), '%Y-%m-%d').strftime('%d'))
            
            a_session = self.write(cr, uid, f.id, {'state': 'Active','date_started': datetime.date.today(),'started_by':uid})
            
            for year in range(s_year,e_year):
                if year == s_year:
                    state = 'Active'
                else:
                    state = 'Draft'
                
                session_start = str(year) +'-'+str(s_month)+'-'+str(s_day)
                session_end = str(int(year+1)) +'-'+str(e_month)+'-'+str(e_day)
                create_session = self.pool.get('sms.session').create(cr,uid,{
                        'start_date':session_start,
                        'end_date':session_end,
                        'state':state,
                          'academic_session_id':f.id
                        })
            return
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
       
        for f in self.browse(cr, uid, ids, context=context):
            state = ''
            start_date = f.start_date
            end_date = f.end_date
           
            s_year = int(datetime.datetime.strptime(str(f.start_date), '%Y-%m-%d').strftime('%Y'))
            e_year = int(datetime.datetime.strptime(str(f.end_date), '%Y-%m-%d').strftime('%Y'))
            result[f.id] = str(s_year) + "-" + str(e_year)
        return result
    
    
    _name = 'sms.academics.session'
    _description = "Stores academics session for an institue, e.g session 2013-2014."
    _columns = {
        'name':fields.function(_set_name, method=True, store = True, size=256, string='Code',type='char'), 
        'session_ids':fields.one2many('sms.session','academic_session_id','Session'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'date_started':fields.date('Started On',readonly = True),
        'started_by':fields.many2one('res.users','Started By',readonly = True),
        'date_closed':fields.date('Closed On',readonly = True),
        'closed_by':fields.many2one('res.users','Closed By',readonly = True),
        'state': fields.selection([('Draft', 'Draft'),('Active', 'Active'),('Closed', 'Closed')], 'State', readonly = True),
    } 
    _defaults = {  'state': 'Draft','name':'New Academic Session'}
    _sql_constraints = [('name_unique', 'unique (name)', """ Academic Session Must be Unique.""")]
sms_academics_session()


class sms_session(osv.osv):
    """
    This object defines academic years/sessions within an academic session
    """
    
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = {}
        year_id = super(osv.osv, self).create(cr, uid, vals, context)
        for f in self.browse(cr, uid, [year_id], context=context):
            #load session months
            self.pool.get('sms.session').load_session_months(cr,uid,year_id)
        return

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
#         rec_session = self.browse(cr, uid, ids, context=context)
#         for record in rec_session:
#             calendar_ids = self.pool.get('sms.academiccalendar').search(cr, uid, [('session_id','=',record.id),('state','=','Complete')])
#             for cal_id in  calendar_ids:
#                 cal_std_ids = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('name','=',cal_id),('state','=','Promoted')])
#                 for std_class in cal_std_ids:
#                     sub_std = self.pool.get('sms.student.subject').search(cr, uid, [('name','=',std_class),('subject_status','=','Current')])
#                     for std_sub in sub_std:
#                         self.pool.get('sms.student.subject').write(cr,uid,std_sub,{'subject_status': 'Pass'}) 
        return True
    
    def unlink(self, cr, uid, ids, context={}, check=True):
        result = []
        for rec in self.browse(cr, uid, ids, context):
            if rec.state == 'Draft':
                classes = self.pool.get('sms.academiccalendar').search(cr, uid, [('session_id','=', rec.id)], context=context)
                if classes:
                    raise osv.except_osv(('Not Allowed'), ('Session can only be deleted in Draft state & not used by any class.'))
                else:
                    result = super(sms_session, self).unlink(cr, uid, [rec.id], context=context)
        return result
     
    def start_new_session(self, cr, uid, ids, *args):
        
        obj = self.browse(cr, uid, ids)
        if not obj[0].months_loaded:
             raise osv.except_osv(('Stop'), ('Please! First Load Session Months' ))
        else:
            active_sessions = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
            if active_sessions:
                sess = ''
                for f in active_sessions:
                    rec = self.pool.get('sms.session').browse(cr, uid, f)
                    sess += "-"+rec.name
#                 raise osv.except_osv(('Only 1 Session must be active at a time '), ('Active Session:'+sess))
            self.write(cr, uid, ids, {'state': 'Active'})
        return True
    
    def load_session_months(self, cr, uid, ids, *args):
        obj = self.browse(cr, uid, ids)
        monthlist = []
        for m in self.browse(cr, uid, [ids]):
            if not m.session_months:
                stmonth = int(datetime.datetime.strptime(str(m.start_date), '%Y-%m-%d').strftime('%m'))
                stmonth_year = int(datetime.datetime.strptime(str(m.start_date), '%Y-%m-%d').strftime('%Y'))
                endmonth = datetime.datetime.strptime(str(m.end_date), '%Y-%m-%d').strftime('%m')
    
                if int(stmonth) < int(endmonth):
                    for stmonth in range(int(stmonth),int(endmonth)+1):
                        stmonth = str(stmonth) +"#"+str(stmonth_year)
                        monthlist.append(stmonth)
                elif  int(stmonth) > int(endmonth) or int(stmonth) == int(endmonth):
                    for stmonth in range(int(stmonth),12+1):
                        stmonth = str(stmonth) +"#"+str(stmonth_year)
                        monthlist.append(stmonth)
                    for stmonth in range(1,int(endmonth)+1):
                        stmonth = str(stmonth) +"#"+str((int(stmonth_year) + 1))
                        monthlist.append(stmonth)
                for months in monthlist:
                   month_yr = months.split('#')
                   month = month_yr[0]
                   year = month_yr[1]
                   
                   create = self.pool.get('sms.session.months').create(cr,uid,{
                            'session_id':m.id,
                            'session_month_id':month,
                            'session_year':year,                                                    
                            })
            self.write(cr, uid, ids, {'months_loaded': 'True'})
        return True
    
    def close_this_session(self, cr, uid, ids, *args):
        """
        Session is closed with an academic year has come to an end, all results are declared, and no pending issues remains in the current session
        if a session is closed with some pending issues, it will be treated like in previous session.
        """
        obj = self.browse(cr,uid,ids)
        for f in obj:
            acad_cals = self.pool.get('sms.academiccalendar').search(cr, uid, [('state','=','Active'),('session_id','=',ids)])
            if acad_cals:
                for idss in acad_cals:
                    close_class = self.pool.get('sms.academiccalendar').write(cr, uid, [idss], {'state': 'Complete','date_closed': datetime.date.today(),'closed_by':uid})
                    subjects = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=',idss),('state','=','Current')])
                    if subjects:
                        for sub in subjects:
                            close_subjects = self.pool.get('sms.academiccalendar.subjects').write(cr, uid, sub, {'state': 'Closed'})
        
        self.write(cr, uid, ids, {'state': 'Previous','date_session_closed':datetime.date.today(),'session_closed_by':uid})
        return True
    
    def set_code(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            sdate = obj.start_date
            edate = obj.end_date
            if edate <= sdate:
                raise osv.except_osv(('Session '), ('Session End date must be greater than Start date.' ))
            else:
                year = sdate.split('-')
                acad_session = obj.academic_session_id.name
                arr = acad_session.split('-')
                result[obj.id] = year[0]+' -(Session: '+str(arr[0][2:])+'-'+str(arr[1][2:])+')'
        return result
    
    def load_students_from_excel(self, cr, uid, data, context):
        workbook = xlrd.open_workbook('/home/baharali/Desktop/Students.xls')
        worksheet = workbook.sheet_by_name('Student')
        rows = worksheet.nrows - 1
        cells = worksheet.ncols - 1
        row = 5
        while row < rows:
            #print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 1)
            
            sql = """SELECT id from sms_academiccalendar 
            where class_id = (SELECT id from sms_classes where sms_classes.desc = '""" + str(worksheet.cell_value(row, 6)).strip() + """')"""
            cr.execute(sql)
            academic_id = cr.fetchone()[0]
            
            student_id = self.pool.get('sms.student').create(cr, uid, {
                'name': worksheet.cell_value(row, 4),
                'registration_no': str(academic_id) + "-" +  str(worksheet.cell_value(row, 3)),
                'gender': worksheet.cell_value(row, 18),
                #'birthday': worksheet.cell_value(row, 20),
                'blood_grp': worksheet.cell_value(row, 21),
                'father_name': worksheet.cell_value(row, 5),
                'father_nic': worksheet.cell_value(row, 7),
                'phone': worksheet.cell_value(row, 8),
                'cell_no': worksheet.cell_value(row, 9),
                'cur_address': str(worksheet.cell_value(row, 10)) + ", " + str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)),
                'cur_city': 'Peshawar', 
                'cur_country': 179,
                'permanent_address': str(worksheet.cell_value(row, 10)) + ", " + str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)),
                'permanent_city': 'Peshawar', 
                'permanent_country': 179, 
                #'admitted_on': '201-10-01',
                'admitted_to_class': academic_id,
                'previous_school': worksheet.cell_value(row, 16),
                'state': 'Admitted',
                'admitted_on': '2013-04-01', 
                'fee_type': 'normal', }, context=context)
            
            
            student_semester_id = self.pool.get('sms.academiccalendar.student').create(cr, uid, {
                'name': academic_id,
                'std_id': student_id,
                'state': 'Current', 
                'date_registered': '2013-04-01',}, context=context)
            
            registration_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr, uid, student_semester_id,context = None)
            self.pool.get('sms.student').write(cr, uid, student_id, {'registration_no': registration_no})
            
            subject_ids = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=', academic_id)], context=context)
            subject_objects = self.pool.get('sms.academiccalendar.subjects').browse(cr, uid, subject_ids, context=context)
            
            for subject in subject_objects: 
                self.pool.get('sms.student.subject').create(cr, uid, {
                    'student': student_semester_id,
                    'subject': subject.id,
                    'subject_status': 'Current',}, context=context)       

            row += 1
        return {}
    
    def get_month_name(self, cr, uid,month):
        if month == 1:
            return "January"
        elif  month == 2:
            return "February"
        elif  month == 3:
            return "March"
        elif  month == 4:
            return "April"
        elif  month == 5:
            return "May"
        elif  month == 6:
            return "June"
        elif  month == 7:
            return "July"
        elif  month == 8:
            return "August"
        elif  month == 9:
            return "September"
        elif  month == 10:
            return "October"
        elif  month ==11:
            return "November"
        elif  month == 12:
            return "December"

    def set_date_format(self, cr, uid,dated):
        arr = dated.split('-')
        mname = self.pool.get('sms.session').get_month_name(cr,uid,int(arr[1]))
        dated = arr[2]+'-'+mname+'-'+arr[0]
        return dated

    _name = 'sms.session'
    _description = "This object defines academic years"
    _columns = {
        'name':fields.function(set_code, method=True,store = True, size=256, string='Code',type='char'),
        'start_date': fields.date("Start",required=True) ,
        'end_date': fields.date("End",required=True),
        'academic_session_id':fields.many2one('sms.academics.session','Academic Session'),
        'session_months':fields.one2many('sms.session.months','session_id','Months'),
        'months_loaded':fields.boolean('Month Loaded'),
        'acad_cals':fields.one2many('sms.academiccalendar','session_id','Academic Calendars'),
        'date_session_stared':fields.date("started on"),
        'date_session_closed':fields.date("Closed on"),
        'session_started_by':fields.many2one('res.users','Started By:'),
        'session_closed_by':fields.many2one('res.users','Closed By'),
        'state': fields.selection([('Draft', 'Draft'),('Active', 'Active'),('Previous', 'Previous')], 'State', readonly = True, help='Session State'),
    }
    _defaults = {  'state': 'Draft'}
    _sql_constraints = [('name_unique', 'unique(name,academic_session_id)', 'Session for the starting year already exists, please select a different year.')]

class sms_session_months(osv.osv):
    """
    This ojects stores months of a session
    """
    def _get_session_month_from_calendar_month(self, cr, uid, year, month):
        result = []
        my_dict = {'session':'','acad_session':'','session_month':''}
        print "month",month
        print "year",year
        
        #first fine month id from sms_months
        month_id = self.pool.get('sms.month').search(cr,uid,[('code','=',month)])
        if month_id:
            session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_month_id','=',month_id[0]),('session_year','=',str(year))])   
            if session_months:
                rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months[0]) 
                print "rec_months.session_id.id",rec_months.session_id
                print "rec_months.session_id.id",rec_months.session_id
        
                my_dict['session'] = rec_months.session_id.id
                my_dict['session_month'] = rec_months.session_id.id
                result.append(my_dict)
                return result
            else:
                raise osv.except_osv(('Session Month Not Found'), ('You may have selected a start date that is beyond this session'))
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
                result[f.id] = str(f.session_month_id.name) + "-" + str(f.session_year) 
        return result
    
    def is_leap_year(self,year):
        year = int(year)
        if year % 100 != 0 and year % 4 == 0:
            return True
        elif year % 100 == 0 and year % 400 == 0:
            return True
        else:
            return False
    
    def get_month_end_date(self, cr,uid,month,year):
        endate = ''
        month = int(month)
        is_leap_year = self.is_leap_year(year)
        
        if month == 1:
            endate = '01/31'
        elif month == 2:
            if is_leap_year:
                 endate = '02/29'
            else:     
                endate = '02/28'
        elif month == 3:
           endate = '03/31'
        elif month == 4:
           endate = '04/30'
        elif month == 5:
            endate = '05/31'
        elif month == 6:
           endate = '06/30'
        elif month == 7:
           endate = '07/31'
        elif month == 8:
            endate = '08/31'
        elif month == 9:
            endate = '09/30'
        elif month == 10:
           endate = '10/31'
        elif month == 11:
           endate = '11/30'
        elif month == 12:
            endate = '12/31'
            
        return endate
    
    _name = 'sms.session.months'
    _description = "stores months of a session"
    _columns = {
        'name':fields.function(_set_name, method=True, store = True, size=256, string='Code',type='char'), 
        'session_id':fields.many2one('sms.session', 'session'),
        'session_month_id': fields.many2one('sms.month', 'Month'),
        'session_year': fields.char('Year'),  
    } 
#     _sql_constraints = [('name_unique', 'unique (session_id,session_month_id)', """ Session month name must be Unique.""")]
sms_session_months()


class sms_class_section(osv.osv):
    """
    This object defines classes section
    """
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
       
        return True
    _name = 'sms.class.section'
    _description = "This object store generic section of class"
    _columns = {
        "name": fields.char("Section", size=32), 
        "active": fields.boolean('Active'),    
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """ Section name must be Unique.""")]

class sms_year(osv.osv):
    """
    Stores Years
    """
    _name = 'sms.year'
    _description = "This object store Years"
    _columns = {
        "name": fields.char("Code", size=32), 
        "active": fields.boolean('Active'),    
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """ Year Already Exists.""")]
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        
class sms_month(osv.osv):
    """
    Stores Months
    """
    _name = 'sms.month'
    _description = "This object store Months"
    _columns = {
        "name":fields.char("Name", size=32),
        'code':fields.char("Code", size=32),
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """ Month Already Exists.""")]

class sms_subject(osv.osv):
    """
    This object defines subjects
    """
    _name = 'sms.subject'
    _description = "This object store generic suject"
    _columns = {
        "name": fields.char("Subject", size=32), 
        "desc": fields.char("Description", size=32),  
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """ Subject name must be Unique.""")]
    
class sms_classes(osv.osv):
    """
    This object defines classes of an institute
    """
    _name = 'sms.classes'
    _description = "This object store generic classes"
    _columns = {
        "name": fields.char("Class", size=32, required=True), 
        "desc": fields.char("Description", size=32, required=True),
        "alias": fields.char("Alias", size=32, required=True),
        "script": fields.selection([('st', 'st'),('nd', 'nd'),('rd', 'rd'),('th', 'th')], 'Script'),
        'category': fields.selection([('Primary', 'Primary'),('Middle', 'Middle'),('High', 'High'),('Intermediate', 'Intermediate')], 'Category'),          
        'grading_policy': fields.one2many('sms.grading.policy', 'class_id' ,'Grading Policy'),
        'grading_scheme': fields.one2many('sms.grading.scheme', 'class_id' ,'Grading Scheme'),
        'sequence': fields.integer('Sequence No'),
            
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """ Class name must be Unique.""")]    

    ###################### Grading Policy #######################
class sms_grading_policy(osv.osv):
    """This object is used to store Class Grading Policy"""
    
    _name = 'sms.grading.policy'
    _columns = {
        'name': fields.char('Subject Grade', size=150),
        'lower_limit': fields.float('Lower Limit'),
        'upper_limit': fields.float('Upper Limit'),
        'grade_point': fields.float('Grade Point'),
        'subject_remarks': fields.char('Subject Remarks', size=150),
        'class_id' :fields.many2one('sms.classes', 'Class'),
    }
    _defaults = {
        'lower_limit': lambda *a: 0,
        'upper_limit': lambda *a: 100,
    }
sms_grading_policy()

###################### Grading Scheme #######################

class sms_grading_scheme(osv.osv):
    """This object is used to store Class Grading Scheme"""
    
    def set_name(self, cr, uid, ids, name, args, context=None):
            result = {}
            for obj in self.browse(cr, uid, ids, context=context):
                effective_from = (parser.parse(obj.effective_from)).strftime('%B, %Y')
                if obj.effective_to:
                    effective_to = (parser.parse(obj.effective_to)).strftime('%B, %Y')
                else:
                    effective_to = "Present" 
                result[obj.id] = "Grading Scheme (" + str(effective_from) + " To " + str(effective_to) + ")"
            return result    
        
    _name = 'sms.grading.scheme'
    _columns = {
        'name': fields.function(set_name, method=True,  string='Grading Scheme',type='char'),
        'effective_from': fields.date('Effective From', required=True),
        'effective_to': fields.date('Effective To'),
        'class_id' :fields.many2one('sms.classes', 'Class'),
        'grading_scheme_lines': fields.one2many('sms.grading.scheme.line', 'grading_scheme' ,'Grading Scheme Lines'),
    }
    _defaults = {
        
    }
sms_grading_scheme()

    ###################### Grading Scheme Line #######################
class sms_grading_scheme_line(osv.osv):
    """This object is used to store Class Grading Scheme Line"""
    
    _name = 'sms.grading.scheme.line'
    _columns = {
        'name': fields.char('Subject Grade', size=150),
        'lower_limit': fields.float('Lower Limit'),
        'upper_limit': fields.float('Upper Limit'),
        'grade_point': fields.float('Grade Point'),
        'subject_remarks': fields.char('Subject Remarks', size=150),
        'grading_scheme' :fields.many2one('sms.grading.scheme', 'Grading Scheme'),
    }
    _defaults = {
        'lower_limit': lambda *a: 0,
        'upper_limit': lambda *a: 100,
    }
sms_grading_scheme_line()

###################### SMS Fee Classes Fees #######################
class smsfee_classes_fees(osv.osv):
    """This object is used to store SMS Fee Class"""
    _name = 'smsfee.classes.fees'
    _columns = {
    }
smsfee_classes_fees()
###################### SMS Fee Classes Fees #######################

class sms_group(osv.osv):
    """This object defines groups of a class e.g Science, Arts etc."""
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        
       
        return True
    _name = 'sms.group'
    _description = "defines new groups of student.."
    _columns = {
        'name':fields.char("Group Name", size=32),
        'desc':fields.char("Description", size=32),
        'active': fields.boolean('Active')
    } 
    _sql_constraints = [('name_unique', 'unique (name)', """Group name must be unique. """)]         
    
class sms_certificate(osv.osv):
    """This object defines certificate format"""
            
    _name = 'sms.certificate'
    _description = "defines certificate"
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'text': fields.text(string = 'Formate'),       
    } 
sms_certificate()    

class sms_student_certificate(osv.osv):
    """This object defines students' certificates."""
            
    _name = 'sms.student.certificate'
    _description = "defines certificate"
    _columns = {
        'name': fields.many2one('sms.student','Student', required=True),
        'certificate': fields.many2one('sms.certificate','Certificate', required=True),
        'certificate_number': fields.char('Certificate Number', required=True),
        'counter':fields.integer('Counter', required=True),      
        'student_issuance':fields.integer('Student Issuance', required=True),      
    } 

sms_student_certificate()    


class sms_student(osv.osv):
    
    """ This object defines students of an institute """
    
    def admisssion_registration(self, cr, uid, ids, context=None):
        ctx = {}
        for f in self.browse(cr,uid,ids):
            if not context:
                ctx = {
                'name':f.name,
                'father_name':f.father_name,
                }
            else:
                ctx = context
                ctx['name'] = f.id
                ctx['father_name'] = f.father_name,
        
        result = {
        'type': 'ir.actions.act_window',
        'name': 'Student Admission',
        'res_model': 'student.admission.register',
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': False,
        'nodestroy': True,
        'target': 'current',
        'context': ctx,
        }
        return result 
    
    def action_admit_student(self, cr, uid, ids, context=None):
        print "action_admit_student"
        return None 
    

    
    
    def unlink(self, cr, uid, ids, context={}, check=True):
        for rec in self.browse(cr, uid, ids, context):
            if rec.state == 'Draft':
                result = super(sms_student, self).unlink(cr, uid, [rec.id], context=context)
            else:
                raise osv.except_osv(('Not Allowed'), ('Student can only be deleted in draft state.\n You can remove a student by using Withdraw wizard.'))
        return result

    def register_std(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'Admitted'})
        return True 
    
    def close_class(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'Pass Out'})
        return True
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        return  dict(self.name_get(cr, uid, ids, context=context))
    
    def _set_default_country(self, cr, uid, context={}):
        contry = self.pool.get('res.country').search(cr, uid, [('name','=','Pakistan')])
        if contry:
            return contry[0]
        else:
            return []
        
    def _get_default_gender(self, cr, uid, ids): 
        user = self.pool.get('res.users').browse(cr, uid, uid, )
        company_id = user.company_id.id
        if company_id:
            rec_company = self.pool.get('res.company').browse(cr,uid,company_id)
            return rec_company.default_gender
        
    def set_registration_counter(self, cr, uid, ids, name, args, context=None):
            result = {}
            for obj in self.browse(cr, uid, ids, context=context):
                counter_val = ""
                counter = str(obj.registration_no).split("-")
                if len(counter)>1:
                    counter = str(counter[1]).split("/")
                    if len(counter)>0:
                        counter_val = counter[0]
                result[obj.id] = counter_val
            return result
    
    def assign_relation(self, cr, uid, ids, context=None):
#        context = {
#        'student_id':ids,
#        'student_class_id': [(0, 0, {'product_id': product_id, 'product_qty': 1})],   
#         }
        result = {
        'type': 'ir.actions.act_window',
        'name': 'Assign Relation',
        'res_model': 'sms.assign.relation',
        'view_type': 'form',
        'view_mode': 'form,tree',
        'view_id': False,
        'target': 'current',
        'domain':[ '|' ,('student_1_1','in',ids),('student_1_2','in',ids)],
        'context': context,
        }
        return result 
    
    def _is_current_user_admin(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        for rule in self.browse(cr, uid, ids, context):
            is_admin = self.pool.get('res.users').search(cr, uid, [('login','=','admin')])
            if is_admin:
                res[rule.id] = True
            else:
                res[rule.id] = False
        return res
           
    _name = 'sms.student'
    _description = "This object store generic classes"
    _columns = {
        'name': fields.char(string = "Student", required = True, size=32),
        'is_loged_user_admin':fields.function(_is_current_user_admin, string='Is Admin Task', type='boolean'),
        'relatives': fields.one2many('sms.student.relation', 'student_id', 'Relatives'),
        'registration_counter': fields.function(set_registration_counter, method=True,  string='Registration Counter',type='integer', store=True),
        'registration_no': fields.char(string = "Registration No.", size=32),
        'gender': fields.selection([('Male', 'Male'),('Female', 'Female')], 'Gender'),
        'birthday': fields.date("Date of Birth"),
        'blood_grp': fields.selection([('A+', 'A+'),('A-', 'A-'),('B+', 'B+'),('B-', 'B-'),('AB+', 'AB+'),('AB-', 'AB-'),('O+', 'O+'),('O-', 'O-')], 'Blood Group'),
        'father_name': fields.char(string = "Father", size=32),
        'father_occupation': fields.char(string = "Father Occupation", size=32),
        'father_nic': fields.char(string = "Father NIC", size=32),
        'religion': fields.char(string = "Religion", size=32),
        'phone': fields.char(string = "Phone No", size=32),
        'cell_no': fields.char(string = "Cell No", size=32),
        'fax_no': fields.char(string = "Fax No", size=32),
        'email': fields.char(string = "Email", size=32),
        'cur_address': fields.char(string = "Street", size=32),
        'cur_city': fields.char(string = "City", size=32), 
        'cur_country': fields.many2one('res.country', 'Country'),
        'permanent_address': fields.char(string = "Street", size=32),
        'permanent_city': fields.char(string = "City", size=32), 
        'permanent_country': fields.many2one('res.country', 'Country'), 
        'domocile': fields.char(string = "Domicile", size=32),
        'login_id': fields.char(string = "Login ID", size=32),
        'password': fields.char(string = "password", size=32), 
        'login_active': fields.boolean('Active'),
        'fee_type':  fields.many2one('sms.feestructure', 'Fee Structure'),
        'admitted_on': fields.date("Admitted On"),
        'admitted_by': fields.many2one('res.users','Admitted By'),
        'classes_history':fields.one2many('sms.academiccalendar.student','std_id','Classes'),
        'reg_nos':fields.one2many('sms.registration.nos','student_id','Registration No'),
        'desired_class':fields.many2one('sms.classes','Apply for Class'),
        'admitted_to_class': fields.many2one('sms.academiccalendar','Admitted To Class', readonly = True),
        'current_class': fields.many2one('sms.academiccalendar','Current Class',select = 1, readonly = True),
        'entrytest_per': fields.float('Entrytest Marks(%)'),
        'previous_school': fields.char(string = "Last School", size=32),
        'reason_leaving': fields.char(string = "Reason For Leaving", size=100),
        'date_withdraw':fields.date('Date Withdraw'),
        'withdraw_by':fields.many2one('res.users','Withdraw By'),
        'date_readmitted':fields.date('Date Withdraw'),
        'state': fields.selection([('Draft', 'Draft'),('Withdraw','Withdraw'),('Admitted', 'Admitted'),('admission_cancel','Admission Cancel'),('drop_out', 'Drop Out'),('deleted', 'deleted'),('slc', 'School Leaving Certificate')], 'State', readonly = True),       
        'image': fields.binary("Photo", help="This field holds the image used as photo for the student, limited to 1024x1024px."),
        'current_state': fields.selection([('Current', 'Current'),('Failed', 'Failed')], 'Current Class State', readonly = True),
        'image': fields.binary("Photo", help="This field holds the image used as photo for the student, limited to 1024x1024px."),
#         'image_medium': fields.function(_get_image, fnct_inv=_set_image, string="Medium-sized photo", type="binary", multi="_get_image",
#                         store = {'sms.student': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),},help="Medium-sized photo of the student. It is automatically "\
#                         "resized as a 128x128px image, with aspect ratio preserved. "\
#                         "Use this field in form views or some kanban views."),
#               
        'reference_ids':fields.one2many('student.reference', 'reference_id', 'References', states={'done':[('readonly',True)]}),
        'previous_school_ids':fields.one2many('student.previous.school', 'previous_school_id', 'Previous School Detail', states={'done':[('readonly',True)]}),
        'family_contact_ids':fields.one2many('student.guardian.contact', 'family_contact_id', 'Guardian Contact', states={'done':[('readonly',True)]}),
        'doctor': fields.char('Doctor Name', size=64, states={'done':[('readonly',True)]} ),
        'designation': fields.char('Designation', size=64),
        'doctor_phone': fields.char('Phone', size=12),
        'blood_group': fields.char('Blood Group', size=12),
        'height': fields.float('Height'),
        'weight': fields.float('Weight'),
        'eye':fields.boolean('Eyes'),
        'ear':fields.boolean('Ears'),
        'nose_throat':fields.boolean('Nose & Throat'),
        'respiratory':fields.boolean('Respiratory'),
        'cardiovascular':fields.boolean('Cardiovascular'),
        'neurological':fields.boolean('Neurological'),
        'muskoskeletal':fields.boolean('Muskoskeletal'),
        'dermatological':fields.boolean('Dermatological'),
        'blood_pressure':fields.boolean('Blood Pressure'),
        'remark':fields.text('Remark'),
        'medical_comment':fields.text('Remark'),
        'achievements_ids' : fields.one2many('student.achievements','student_id','Achievements'),
        'active_subjects' : fields.one2many('sms.student.subject','student_id','Subjects'),
        'certificate_ids' : fields.one2many('sms.student.certificate','name','Certificates'),   
        'form_no':fields.char(string = "Form No", size=32),
        'fee_starting_month' : fields.many2one('sms.session.months', 'Fee Starting Month'),
        'board_reg_no':fields.char(string = "Board Registration No", size=32),
        
    } 
    _defaults = {
        'login_active': False,
        'state': 'Draft',
        'gender':_get_default_gender,
        'entrytest_per':0.0,
        'cur_country': _set_default_country,
        'cur_city':'Peshawar'
    }
    _sql_constraints = [('name_unique', 'unique (registration_no)', """ Student No must be Unique.""")]    

class sms_relation(osv.Model):
    _name = "sms.relation"
    _columns = {
        'name' : fields.char('Relation', size=30, required=True),
        'gender': fields.selection([('Male', 'Male'),('Female', 'Female')], 'Relation Gender', required=True),          
    }
    _sql_constraints = [('unique_record', 'unique (name, gender)', """ Relation must be Unique.""")]    

class sms_assign_relation(osv.Model):
    
    def onchange_student_1_1(self, cr, uid, ids, student, context=None):
        result = {}
        result['student_2_2'] = student
        result['relation_1'] = None
        if student:
            result['gender_1'] = self.pool.get('sms.student').browse(cr, uid, student, context=context).gender
        else:
            result['gender_1'] = None
        return {'value': result}
        
    def onchange_student_1_2(self, cr, uid, ids, student, context=None):
        result = {}
        result['student_2_1'] = student
        result['relation_2'] = None
        if student:
            result['gender_2'] = self.pool.get('sms.student').browse(cr, uid, student, context=context).gender
        else:
            result['gender_2'] = None
        return {'value': result}
        
    def set_relation_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            name = obj.relation_1.name + " : " + obj.relation_2.name 
            result[obj.id] = name
        return result
   
    _name = "sms.assign.relation"
    _columns = {
        'name':  fields.function(set_relation_name, method=True, string='Relation',type='char'), 
        'student_1_1' : fields.many2one('sms.student', 'Student', required=True, domain="[('id','!=',student_1_2),('state','=','Admitted')]"),
        'gender_1' : fields.char('Gender', size=30),
        'label_is_1' : fields.char('is', size=30, required=True, readonly=True),
        'relation_1' : fields.many2one('sms.relation', 'Student', required=True, domain="[('gender','=',gender_1)]"),
        'label_of_1' : fields.char('of', size=30, required=True, readonly=True),
        'student_1_2' : fields.many2one('sms.student', 'Student', required=True, domain="[('id','!=',student_1_1),('state','=','Admitted')]"),
        
        'student_2_1' : fields.many2one('sms.student', 'Student', required=True, domain="[('id','=',student_1_2),('state','=','Admitted')]"),
        'gender_2' : fields.char('Gender', size=30),
        'label_is_2' : fields.char('is', size=30, required=True, readonly=True),
        'relation_2' : fields.many2one('sms.relation', 'Student', required=True, domain="[('gender','=',gender_2)]"),
        'label_of_2' : fields.char('of', size=30, required=True, readonly=True),
        'student_2_2' : fields.many2one('sms.student', 'Student', required=True, domain="[('id','=',student_1_1),('state','=','Admitted')]"),       
    }
    _defaults = {
        'label_is_1': 'is',
        'label_is_2': 'is',
        'label_of_1': 'of',
        'label_of_2': 'of',
        }

    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)       
        records = self.browse(cr, uid, [result], context=context)        
        for record in records:
            self.pool.get('sms.student.relation').create(cr, uid, {
                'student': record.student_1_1.id,
                'student_id': record.student_1_2.id,
                'gender': record.gender_1,
                'relation':record.relation_1.id,
                'assign_relation':record.id,
               })

            self.pool.get('sms.student.relation').create(cr, uid, {
                'student': record.student_2_1.id,
                'student_id': record.student_2_2.id,
                'gender': record.gender_2,
                'relation':record.relation_2.id,
                'assign_relation':record.id,
               })

        return result
  
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        objs = self.browse(cr, uid, ids, context=context)
        for record in objs:
            relation_ids = self.pool.get('sms.student.relation').search(cr, uid, [('assign_relation','=',record.id),('student','=',record.student_1_1.id)])
            rel_objs = self.pool.get('sms.student.relation').browse(cr, uid, relation_ids, context=context)
            for rel_obj in rel_objs:
                self.pool.get('sms.student.relation').write(cr, uid, [rel_obj.id], {
                    'student': record.student_1_1.id,
                    'student_id': record.student_1_2.id,
                    'gender': record.gender_1,
                    'relation':record.relation_1.id,
                    'assign_relation':record.id,
                   })
            
            relation_ids = self.pool.get('sms.student.relation').search(cr, uid, [('assign_relation','=',record.id),('student','=',record.student_2_1.id)])
            rel_objs = self.pool.get('sms.student.relation').browse(cr, uid, relation_ids, context=context)
            for rel_obj in rel_objs:
                self.pool.get('sms.student.relation').write(cr, uid, [rel_obj.id], {
                    'student': record.student_2_1.id,
                    'student_id': record.student_2_2.id,
                    'gender': record.gender_2,
                    'relation':record.relation_2.id,
                    'assign_relation':record.id,
                    })
        return result
    
    def unlink(self, cr, uid, ids, context={}, check=True):
        objs = self.browse(cr, uid, ids, context=context)
        for record in objs:
            relation_ids = self.pool.get('sms.student.relation').search(cr, uid, [('assign_relation','=',record.id)])
            self.pool.get('sms.student.relation').unlink(cr, uid, relation_ids, context)
        result = super(osv.osv, self).unlink(cr, uid, ids, context)
        return result

    
class sms_student_relation(osv.Model):
    
    def set_relation_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            name = obj.student.name + " is a " + obj.relation.name + " of " + obj.student_id.name   
            result[obj.id] = name
        return result
 
    def onchange_student(self, cr, uid, ids, student, context=None):
        result = {}
        result['relation'] = None
        if student:
            result['gender'] = self.pool.get('sms.student').browse(cr, uid, student, context=context).gender
        else:
            result['gender'] = None
        return {'value': result}

    _name = "sms.student.relation"
    _columns = {
        'name':  fields.function(set_relation_name, method=True, string='Relation',type='char'), 
        'student' : fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", required=True),
        'gender' : fields.char('Gender', size=30, required=True),
        'student_id' : fields.many2one('sms.student', 'Student', required=True),
        'relation' : fields.many2one('sms.relation', 'Relation', domain="[('gender','=',gender)]", required=True),
        'assign_relation' : fields.many2one('sms.assign.relation', 'Assigned Relation'),
    }
    _sql_constraints = [('unique_record', 'unique (student,student_id,relation)', """ Relation must be Unique.""")]    

class student_achievements(osv.Model):
    _name = "student.achievements"
    _columns = {
        'student_id' : fields.many2one('sms.student', 'Student'),
        'description' : fields.char('Description',size=50),
        'certificate' : fields.binary('Certificate',required =True)
    }
class sms_registration_nos(osv.Model):
    _name = "sms.registration.nos"
    _columns = {
        'student_id' : fields.many2one('sms.student', 'Student'),
        'name' : fields.char('Registration No',size=50),
        'class_category': fields.selection([('Primary', 'Primary'),('Middle', 'Middle'),('High', 'High')], 'Category'),          
        'is_active' : fields.boolean('Active')
    }   
       

class student_previous_school(osv.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"
    _columns = {
        'previous_school_id': fields.many2one('sms.student', 'Student'),
        'name': fields.char('Name', size=64, required=True),
        'registration_no': fields.char('Registration No.', size=12, required=True),
        'admission_date': fields.date('Admission Date'),
        'exit_date': fields.date('Exit Date'),
    }
 
student_previous_school()

class student_reference(osv.Model):
    ''' All references of student'''
    _name = "student.reference"
    _description = "Student References"
    _columns = {
        'reference_id': fields.many2one('sms.student', 'Student'),
        'name': fields.char('First Name', size=64, required=True),
        'middle': fields.char('Middle Name', size=64, required=True),
        'last': fields.char('Surname', size=64, required=True),
        'designation': fields.char('Designation', size=12, required=True),
        'phone': fields.char('Phone', size=12, required=True),
        'gender':fields.selection([('male','Male'), ('female','Female')], 'Gender'),
    }

student_reference()  

class student_guardian_contact(osv.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.guardian.contact"
    _description = "Student Family Contact"
    _columns = {
        'family_contact_id': fields.many2one('sms.student', 'Student'),
        'rel_name': fields.selection([('Brother','Brother'), ('Mother','Mother'),('Relative','Relative')], 'Relation', help="Select Name", required=True),
        'name':fields.char('Name',size=20, required=True),
        'phone': fields.char('Phone', size=20, required=True),
        'email': fields.char('E-Mail', size=100),
    }
student_guardian_contact()

class sms_academiccalendar(osv.osv):
    """This object combines sms.session,sms.classes,sms.classes section to form a new class in a new session with unique class section no."""
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        
        for f in self.browse(cr, uid, ids):
            acad_cal_state = f.state
            if f.state == 'Active':
                #Step1: make all draft subject to current in this acad cal,
                cal_subjects = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=',ids[0]),('state','=','Draft')])
                if cal_subjects:
                    for subject in cal_subjects:
                        make_current =self.pool.get('sms.academiccalendar.subjects').write(cr, uid, subject, {'state':'Current'})
                        if make_current:
                            #step 2 add all these subjects to student of this acad_cal
                            acad_cal_students = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('name','=',ids[0]),('state','=','Current')])
                            if acad_cal_students:
                                rec_cal_students = self.pool.get('sms.academiccalendar.student').browse(cr, uid,acad_cal_students)
                                for cal_student in rec_cal_students:
                                    add_subjects = self.pool.get('sms.student.subject').create(cr, uid, {
                                                    'student': cal_student.id,
                                                    'student_id': cal_student.std_id.id,
                                                    'subject':subject,
                                                    'subject_status':'Current',
                                                    })
                            #add subjects to exams
                            active_exams_ids = self.pool.get('sms.exam.datesheet').search(cr, uid, [('academiccalendar','=',ids[0])])
                            for exm in active_exams_ids:
                                date_sheet_lines = self.pool.get('sms.exam.datesheet.lines').create(cr, uid, {
                                                'name': exm,
                                                'subject': subject,
                                                })
                            
                            
        return True
    
    def _get_default_group(self, cr, uid, context={}):
        grp = self.pool.get('sms.group').search(cr, uid, [('name','=','No group')])
        if grp:
            return grp[0]
        else:
            return []
        
    
        
    def _get_default_section(self, cr, uid, context={}):
        sec = self.pool.get('sms.class.section').search(cr, uid, [('name','=','Section A')])
        if sec:
            return sec[0]
        else:
            return []
    
    def _get_active_session_from_acad_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active'),])
        if ssn:
            return ssn[0]
        else:
            return []
    def set_class_name(self, cr, uid, ids, name, args, context=None):
            result = {}
            for obj in self.browse(cr, uid, ids, context=context):
                cls = obj.class_id.name
                session = obj.acad_session_id.name
                section = obj.section_id.name
                string = str(cls)+' - '+str(section)+' ('+str(session)+')'
                result[obj.id] = string
            return result
    
    def onchange_max_student_to_set_class_name(self, cr, uid, ids):
            result = {}
            for obj in self.browse(cr, uid, ids):
                cls = obj.class_id.name
                session = obj.acad_session_id.name
                section = obj.section_id.name
                string = str(cls)+' - '+str(section)+' ('+str(session)+')'
                sql = """sms_academiccalendar set name = """+str(string)+"""where id = """+str(f.id)
                cr.execute(sql)
            return result
    
    def onchange_academic_session(self, cr, uid, ids, ac_session, context=None):
        result = {}
        session_id = self.pool.get('sms.session').search(cr, uid, [('academic_session_id','=', ac_session),('state','=', 'Active')])
        if session_id:
            result['session_id'] = session_id[0]
            return {'value': result}
        else:
            return {}
    
    def update_class_strength(self, cr, uid, ids, name, args, context=None):
        result = {}
        acad_cal = self.browse(cr, uid,ids)
        for f in acad_cal:
            sql = """select count(*) from sms_academiccalendar_student where "name" = """+str(f.id)+"""AND state = 'Current'"""
            cr.execute(sql)
            cnt = cr.fetchone()
            result[f.id] = cnt[0]
        return result   
    
    
    def change_student_class(self, cr, uid, ids,class_id,new_class_id,new_fs,f_start_month,xx):
        ftlist = []
                    
        
        #delete this from receiptbooklines
        cls_fees_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[])
        print "rrrrrrrrrr", cls_fees_ids
        for rec in cls_fees_ids:
            del_fee1 = """DELETE FROM smsfee_receiptbook_lines WHERE student_fee_id ="""+str(rec)
            cr.execute(del_fee1)
            cr.commit()
        #Delete this fee from student fee
        del_fee2 = self.pool.get('smsfee.studentfee').unlink(cr,uid,rec)
        if del_fee2:
            #delete student subjects
            std_sub_ids = self.pool.get('sms.student.subject').search(cr,uid,[('student_id','=',ids),('subject_status','=','Current')])
            for std_sub in std_sub_ids:
                self.pool.get('sms.student.subject').unlink(cr,uid,std_sub)
            #Delete Class History
            student_class_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',ids),('name','=',class_id),('state','=',"Current")])
            if student_class_id:
                del_class = self.pool.get('sms.academiccalendar.student').unlink(cr,uid,student_class_id)
                if del_class:
                    std = self.pool.get('sms.student').browse(cr,uid,obj.name.id).name
                    new_cls_id = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                    'name':new_class_id,                                                       
                    'std_id':ids,
                    'date_registered':datetime.date.today(), 
                    'state':'Current' })
                    if new_cls_id:
                            self.pool.get('sms.student').write(cr, uid, [ids], {'current_class':new_class_id,})
                            #add subjects to students
                            acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',new_class_id),('state','!=','Closed')])
                            for sub in acad_subs:
                                add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                                'student': new_cls_id,
                                'student_id': ids,
                                'subject': sub,
                                'subject_status': 'Current'})
                            
                            #Now add newfees added from wziard
                            sql_ft = """SELECT id from smsfee_feetypes WHERE subtype IN('at_admission','Monthly_Fee','Annual_fee')"""
                            cr.execute(sql_ft)
                            ft_ids = cr.fetchall() 
                            
                            for ft in ft_ids:
                                ftlist.append(ft[0])
                            ftlist = tuple(ftlist)
                            ftlist = str(ftlist).rstrip(',)')
                            ftlist = ftlist+')'
            #               first insert all non motnly fees(search for fee with subtype at_admission) 
                            if ft_ids:
                                sqlfee1 =  """SELECT smsfee_classes_fees.id from smsfee_classes_fees
                                            INNER JOIN smsfee_feetypes
                                            ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                            WHERE smsfee_classes_fees.academic_cal_id ="""+str(new_class_id)+"""
                                            AND smsfee_classes_fees.fee_structure_id="""+str(new_fs)+"""
                                            AND smsfee_feetypes.subtype <>'Monthly_Fee'
                                            AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
                                cr.execute(sqlfee1)
                                fees_ids = cr.fetchall()  
                                if fees_ids: 
                                    late_fee = 0
                                    for idds in fees_ids:
                                        obj2 = self.pool.get('smsfee.classes.fees').browse(cr,uid,idds[0])
                                        crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                        'student_id': ids,
                                        'acad_cal_id': new_class_id,
                                        'acad_cal_std_id': new_cls_id,
                                        'date_fee_charged': datetime.date.today(),
                                        'fee_type': obj2.id,
                                        'due_month': f_start_month,
                                        'fee_amount': obj2.amount,
                                        'late_fee': late_fee,
                                        'total_amount': obj2.amount + late_fee,
                                        'paid_amount':0,
                                        'state':'fee_unpaid',
                                        })
                                else:
                                      msg = 'Fee May be defined but not set for New Class:'        
            #                 # now insert all month fee , get it from the classes with a fee structure and then insert
                                sqlfee2 =  """SELECT smsfee_classes_fees.id from smsfee_classes_fees
                                            INNER JOIN smsfee_feetypes
                                            ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                            WHERE smsfee_classes_fees.academic_cal_id ="""+str(new_class_id)+"""
                                            AND smsfee_classes_fees.fee_structure_id="""+str(new_fs)+"""
                                            AND smsfee_feetypes.subtype ='Monthly_Fee'
                                            AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
                        
                                cr.execute(sqlfee2)
                                fees_ids2 = cr.fetchall() 
                                #get update month of the class
                                updated_month = new_cal_obj.fee_update_till.id
                                #Now brows its session month ids, that will be saved as fee month 
                                session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',new_cal_obj.session_id.id),('id','>=',std.fee_starting_month.id)]) 
                                rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)       
                                for month1 in rec_months:
                                    if month1.id <= f_start_month:
                                        late_fee = 0
                                        for fee in fees_ids2:
                                            obj3 = self.pool.get('smsfee.classes.fees').browse(cr,uid,fee[0])
                                            create_fee2 = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                            'student_id': obj.name.id,
                                            'acad_cal_id': obj.sms_academiccalendar_to.id,
                                            'date_fee_charged': datetime.date.today(),
                                            'acad_cal_std_id': new_cls_id,
                                            'fee_type': obj3.id,
                                            'fee_month': month1.id,
                                            'due_month': month1.id,
                                            'fee_amount': obj3.amount,
                                            'total': obj3.amount + late_fee,
                                             'state':'fee_unpaid',
                                            })
                                        
                            else:
                                raise osv.except_osv(('No Fee Found'),('Please Define a Fee For students promotion'))
       
        
        return

    def unlink(self, cr, uid, ids, context={}, check=True):
        print "@@@@acd_cal@@@@@",ids,context
        for rec in self.browse(cr, uid, ids, context):
            print "inside for"
            result = super(osv.osv, self).unlink(cr, uid, ids, context=context)
        return result     

    _name = 'sms.academiccalendar'
    _description = "Crates new class in a new session."
    _columns = {
        'name':  fields.function(set_class_name, method=True, store = True ,string='Class',type='char'), 
        'acad_session_id': fields.many2one('sms.academics.session', 'Academic Session',domain="[('state','!=','Closed')]",required=True),
        'session_id': fields.many2one('sms.session', 'Session Year',domain="[('state','!=','Previous'),('academic_session_id','=',acad_session_id)]",required=True),
        'class_id': fields.many2one('sms.classes', 'Class',required=True), 
        'section_id': fields.many2one('sms.class.section', 'Section',required=True),
        'group_id': fields.many2one('sms.group', 'Group',required=True),
        'class_teacher': fields.many2one('hr.employee', 'Class Teacher',required=True),
        'max_stds': fields.integer('Max Students'),
        'cur_strength':fields.function(update_class_strength, method=True, string='Current Strength',type='char'),
        'acad_cal_students': fields.one2many('sms.academiccalendar.student','name','Students'),
        'assigned_subjects': fields.one2many('sms.academiccalendar.subjects','academic_calendar','Subjects'),
        'subjects_loaded':fields.boolean('Subject Loaded'),
        'timetable_created':fields.boolean('Time Table Created'),
        'fee_defined':fields.boolean('Fee Defined'),
        'admission_closed':fields.boolean('Admission Closed'),
        'state': fields.selection([('Draft', 'Draft'),('Active', 'Active'),('Complete', 'Complete')], 'States'),
        'date_started':fields.date('Started On'),
        'started_by':fields.many2one('res.users', 'Started By'),
        'date_closed':fields.date('Closed On'),
        'closed_by':fields.many2one('res.users', 'Closed By'),
        'helptxt':fields.text('Help', readonly = True),
        'exam_ids' :fields.one2many('sms.exam.datesheet', 'academiccalendar', 'Exam', readonly=True),
    } 
    
    _defaults = {
        'max_stds': 40,
        'state': 'Draft',
        'fee_defined':False,
        'section_id':_get_default_section,
        'group_id':_get_default_group,
        'helptxt':'Academic Calender: A Class in current session. \n 1: Create A new Academic Calendar. \n 2: Load subjects to it.\n 3: Start Academic Calendar.\n 4: Admit Student in this Academic Calendar.',
    }
    _sql_constraints = [('name_unique', 'unique (session_id,class_id,section_id)', """Session, Class and Section must be unique. """)]   
    
    def start_class(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context=context)
        session_id = obj[0].session_id.id
        sess_obj = self.pool.get('sms.session').browse(cr, uid,session_id)
        sess_state =sess_obj.state
        sess_name = sess_obj.name
        if sess_state =='Draft':
             raise osv.except_osv(('This Class Belongs to Session'+sess_name),('Which is in Draft State. Please Start This session when current running session is closed. '))
        sub_lst = 'Change Status of Following Subjects.\n' 
        acad_cal = obj[0].id
        if obj[0].subjects_loaded:
#             Search Draft Subjects before class is started
              draft_subj = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=', acad_cal),('state','=', 'Draft')])
              if draft_subj:
                  for sub in draft_subj:
                    self.pool.get('sms.academiccalendar.subjects').write(cr, uid, sub, {'state': 'Current'})
              self.write(cr, uid, ids, {'state': 'Active','date_started':datetime.date.today(),'started_by':uid})
        else:
             raise osv.except_osv(('Session '), ('Load subjects before starting Class.' ))
        return True 
    
    
    def load_subjects(self, cr, uid, ids, context=None):
        for f in self.browse(cr, uid, ids, context=context):
            if f.subjects_loaded:
                 raise osv.except_osv(('Subject Already loaded'),('Subjects for this class are already loaded'))
            else:
                academic_default_ids = self.pool.get('sms.academiccalendar.default').search(cr, uid, [('name','=',f.class_id.id)])
                if academic_default_ids:
                    academic_default_object = self.pool.get('sms.academiccalendar.default').browse(cr, uid, academic_default_ids, context=context)
                     
                    for row in academic_default_object:
                        subject_ids = self.pool.get('sms.academiccalendar.subjects.default').search(cr, uid, [('academic_calendar','=', row.id)], context=context)
                        subject_objects = self.pool.get('sms.academiccalendar.subjects.default').browse(cr, uid, subject_ids, context=context)
                         
                        for record in subject_objects:
                            self.pool.get('sms.academiccalendar.subjects').create(cr, uid, {
                            'subject_id': record.name.id,
                            'academic_calendar': f.id,
                            'total_marks': 100,
                            'passing_marks': 40,
                            'min_require_att': 70,
                            'state': 'Draft',}, context=context)
                         
                        self.write(cr, uid, ids, {'subjects_loaded':True})
                else:
                     raise osv.except_osv(('Class Does not Exist '), ('No Default Class Exists for .'+f.class_id.name))         
        return True 
        
    
#     def load_students_from_excel(self, cr, uid, data, context):
#         workbook = xlrd.open_workbook('/home/inovtec/Desktop/Students.xls')
#         worksheet = workbook.sheet_by_name('Student')
#         rows = worksheet.nrows - 1
#         cells = worksheet.ncols - 1
#         row = 5
#         while row < rows:
#             #print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 1)
#             print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 6)
#             
#             sql = """SELECT id from sms_academiccalendar 
#             where class_id = (SELECT id from sms_classes where sms_classes.desc = '""" + str(worksheet.cell_value(row, 6)).strip() + """')"""
#             cr.execute(sql)
#             academic_id = cr.fetchone()[0]
#             
#             print "academic_id,: ", academic_id 
#             
#         
#             student_id = self.pool.get('sms.student').create(cr, uid, {
#                 'name': worksheet.cell_value(row, 4),
#                 'registration_no': str(academic_id) + "-" +  str(worksheet.cell_value(row, 3)),
#                 'gender': worksheet.cell_value(row, 18),
#                 #'birthday': worksheet.cell_value(row, 20),
#                 'blood_grp': worksheet.cell_value(row, 21),
#                 'father_name': worksheet.cell_value(row, 5),
#                 'father_nic': worksheet.cell_value(row, 7),
#                 'phone': worksheet.cell_value(row, 8),
#                 'cell_no': worksheet.cell_value(row, 9),
#                 'cur_address': str(worksheet.cell_value(row, 10)) + ", " + str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)),
#                 'cur_city': 'Peshawar', 
#                 'cur_country': 179,
#                 'permanent_address': str(worksheet.cell_value(row, 10)) + ", " + str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)),
#                 'permanent_city': 'Peshawar', 
#                 'permanent_country': 179, 
#                 #'admitted_on': '201-10-01',
#                 'admitted_to_class': academic_id,
#                 'previous_school': worksheet.cell_value(row, 16),
#                 'state': 'Admitted',
#                 'admitted_on': '2013-04-01', 
#                 'fee_type': 'normal', }, context=context)
#             
#             
#             student_semester_id = self.pool.get('sms.academiccalendar.student').create(cr, uid, {
#                 'name': academic_id,
#                 'std_id': student_id,
#                 'state': 'Current', 
#                 'date_registered': '2013-04-01',}, context=context)
#             
#             registration_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr, uid, student_semester_id,context = None)
#             self.pool.get('sms.student').write(cr, uid, student_id, {'registration_no': registration_no})
#             
#             subject_ids = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=', academic_id)], context=context)
#             subject_objects = self.pool.get('sms.academiccalendar.subjects').browse(cr, uid, subject_ids, context=context)
#             
#             for subject in subject_objects: 
#                 self.pool.get('sms.student.subject').create(cr, uid, {
#                     'student': student_semester_id,
#                     'subject': subject.id,
#                     'subject_status': 'Current',}, context=context)       
# 
#             row += 1
#         return {}

    
    def load_timetable(self, cr, uid, ids, context=None):
        academic_object = self.browse(cr, uid, ids, context=context)
        timetable_default_ids = self.pool.get('sms.timetable.default').search(cr, uid, [('name','=', academic_object[0].class_id.id)], context=context)
        timetable_default_object = self.pool.get('sms.timetable.default').browse(cr, uid, timetable_default_ids, context=context)
        
        sub_query = """SELECT id, teacher_id from sms_academiccalendar_subjects
            where academic_calendar = """ + str(academic_object[0].id)
        cr.execute(sub_query)
        sub_records = cr.fetchall()
        
        sub_list = []
        count = 0
        for sub_record in sub_records:
            sub_list.append(str(sub_record[0]) + ":" + str(sub_record[1]))
            count = count + 1

        for row in timetable_default_object:
            timetable_lines_ids = self.pool.get('sms.timetable.lines.default').search(cr, uid, [('timetable_id','=', row.id)], context=context)
            timetable_lines_objects = self.pool.get('sms.timetable.lines.default').browse(cr, uid, timetable_lines_ids, context=context)
            
            timetable_id = self.pool.get('sms.timetable').create(cr, uid, {
                        'state': 'Draft',
                        'start_date': academic_object[0].session_id.start_date,
                        'end_date': academic_object[0].session_id.end_date,
                        'academic_id': academic_object[0].id,}, context=context)
                
            day_query="""SELECT id, name from sms_day where active = true order by id""" 
            
            cr.execute(day_query)
            day_records = cr.fetchall()
            
            
            time_list = []
            for record in timetable_lines_objects:
                if record.type == 'Period':
                    time_list.append(record.timetable_slot_id.name)
            
            list = self.check_clash_all(cr,uid,sub_list, time_list, count)
            sub_list = list.split(",");
                   
            for day_record in day_records:
                i = 0
                for record in timetable_lines_objects:
                    teacher_id = sub_list[i].split(":")[1]
                    day_id = day_record[0]
                    slot_name = record.timetable_slot_id.name
                     
                    #is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,teacher_id, day_id, slot_name)
                    #if not is_clash:
                    if record.type == 'Period':
                        self.pool.get('sms.timetable.lines').create(cr, uid, {
                        'is_lab': False,
                        'type': record.type,
                        'period_break_no': record.period_break_no,
                        'subject_id': sub_list[i].split(":")[0],
                        'teacher_id': sub_list[i].split(":")[1],
                        'day_id': day_record[0],
                        'timetable_slot_id': record.timetable_slot_id.id,
                        'timetable_id': timetable_id,}, context=context)
                        i = i + 1
                         
                    else:
                        self.pool.get('sms.timetable.lines').create(cr, uid, {
                        'type': record.type,
                        'period_break_no': record.period_break_no,
                        'day_id': day_record[0],
                        'timetable_slot_id': record.timetable_slot_id.id,
                        'timetable_id': timetable_id,}, context=context)
                    if count == i:
                        break
            self.write(cr, uid, ids, {'state': 'timetable_loaded'})
        return True 
    
    def check_clash_all(self, cr, uid, sub_list, slot_list, size, context=None):
        
        break_value = '0'
        is_break = False
        count = 0
        
        for a in range(0, size):
            if is_break:
                if break_value == 'a': 
                    is_break = False
                else: break
            if size == 1:
                is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                if is_clash:
                    break_value = '0'
                    is_break = True
                    break
                return sub_list[a]
                
            else:
                for b in range(0, size):
                    if is_break:
                        if break_value == 'b': 
                            is_break = False
                        else: break
                    if size == 2:
                        if(a != b):
                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                            if is_clash:
                                break_value = 'a'
                                is_break = True
                                break
                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                            if is_clash:
                                break_value = 'a'
                                is_break = True
                                break
                            return sub_list[a] + "," + sub_list[b]
                    else:
                        for c in range(0, size):
                            if is_break:
                                if break_value == 'c': 
                                    is_break = False
                                else: break
        
                            if size == 3:
                                if(a != b and a != c and b != c):
                                    
                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                    if is_clash:
                                        break_value = 'a'
                                        is_break = True
                                        break
                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                    if is_clash:
                                        break_value = 'b'
                                        is_break = True
                                        break
                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                    if is_clash:
                                        break_value = 'b'
                                        is_break = True
                                        break
                                    return sub_list[a] + "," + sub_list[b] + "," + sub_list[c]
                            else:
                                for d in range(0, size):
                                    if is_break:
                                        if break_value == 'd': 
                                            is_break = False
                                        else: break
            
                                    if size == 4:
                                        if(a != b and a != c and a != d and b != c  and b != d and c != d):
                                            
                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                            if is_clash:
                                                break_value = 'a'
                                                is_break = True
                                                break
                                           
                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                            if is_clash:
                                                break_value = 'b'
                                                is_break = True
                                                break
                                            
                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                            if is_clash:
                                                break_value = 'c'
                                                is_break = True
                                                break
                                            
                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                            if is_clash:
                                                break_value = 'c'
                                                is_break = True
                                                break
                                            
                                            return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d]
                                    else:
                                        for e in range(0, size):
                                            if is_break:
                                                if break_value == 'e': 
                                                    is_break = False
                                                else: break
                                            if size == 5:
                                                if(a != b and a != c and a != d and a != e and b != c  and b != d and b != e and c != d and c != e and d != e):
                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                    if is_clash:
                                                        break_value = 'a'
                                                        is_break = True
                                                        break
                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                    if is_clash:
                                                        break_value = 'b'
                                                        is_break = True
                                                        break
                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                    if is_clash:
                                                        break_value = 'c'
                                                        is_break = True
                                                        break
                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                    if is_clash:
                                                        break_value = 'd'
                                                        is_break = True
                                                        break
                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                    if is_clash:
                                                        break_value = 'd'
                                                        is_break = True
                                                        break

                                                    
                                                    return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d]+ "," + sub_list[e]
                                            else:
                                                for f in range(0, size):
                                                    if is_break:
                                                        if break_value == 'f': 
                                                            is_break = False
                                                        else: break
                                                    if size == 6:
                                                        if(a != b and a != c and a != d and a != e and a != f and b != c  and b != d and b != e and b != f and c != d and c != e and c != f and d != e and d != f and e != f):
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                            if is_clash:
                                                                break_value = 'a'
                                                                is_break = True
                                                                break
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                            if is_clash:
                                                                break_value = 'b'
                                                                is_break = True
                                                                break
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                            if is_clash:
                                                                break_value = 'c'
                                                                is_break = True
                                                                break
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                            if is_clash:
                                                                break_value = 'd'
                                                                is_break = True
                                                                break
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                            if is_clash:
                                                                break_value = 'e'
                                                                is_break = True
                                                                break
                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[f].split(":")[1], slot_list[5])
                                                            if is_clash:
                                                                break_value = 'e'
                                                                is_break = True
                                                                break
                                                            
                                                            return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d]+ "," + sub_list[e]+ "," + sub_list[e]
                                                    else:
                                                        for g in range(0, size):
                                                            if is_break:
                                                                if break_value == 'f': 
                                                                    is_break = False
                                                                else: break
                                                            if size == 7:
                                                                if(a != b and a != c and a != d and a != e and a != f and a != g and b != c  and b != d and b != e and b != f and b != g and c != d and c != e and c != f and c != g and d != e and d != f and d != g and e != f and e != g and f != g ):

                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                                    if is_clash:
                                                                        break_value = 'a'
                                                                        is_break = True
                                                                        break
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                                    if is_clash:
                                                                        break_value = 'b'
                                                                        is_break = True
                                                                        break
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                                    if is_clash:
                                                                        break_value = 'c'
                                                                        is_break = True
                                                                        break
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                                    if is_clash:
                                                                        break_value = 'd'
                                                                        is_break = True
                                                                        break
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                                    if is_clash:
                                                                        break_value = 'e'
                                                                        is_break = True
                                                                        break
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[f].split(":")[1], slot_list[5])
                                                                    if is_clash:
                                                                        break_value = 'f'
                                                                        is_break = True
                                                                        break
                                                                                                                                        
                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[g].split(":")[1], slot_list[6])
                                                                    if is_clash:
                                                                        break_value = 'f'
                                                                        is_break = True
                                                                        break
                                                                    
                                                                    
                                                                    return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d] + "," + sub_list[e] + "," + sub_list[f]+ "," + sub_list[g]
                                                            else:
                                                                for h in range(0, size):
                                                                    if is_break:
                                                                        if break_value == 'h': 
                                                                            is_break = False
                                                                        else: break
                                                                    if size == 8:
                                                                        if(a != b and a != c and a != d and a != e and a != f and a != g and a != h and b != c  and b != d and b != e and b != f and b != g and b != h and c != d and c != e and c != f and c != g and c != h and d != e and d != f and d != g and d != h and e != f and e != g and e != h and f != g and f != h and g != h):
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                                            if is_clash:
                                                                                break_value = 'a'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                                            if is_clash:
                                                                                break_value = 'b'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                                            if is_clash:
                                                                                break_value = 'c'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                                            if is_clash:
                                                                                break_value = 'd'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                                            if is_clash:
                                                                                break_value = 'e'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[f].split(":")[1], slot_list[5])
                                                                            if is_clash:
                                                                                break_value = 'f'
                                                                                is_break = True
                                                                                break
                                                                                                                                                
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[g].split(":")[1], slot_list[6])
                                                                            if is_clash:
                                                                                break_value = 'g'
                                                                                is_break = True
                                                                                break
                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[h].split(":")[1], slot_list[7])
                                                                            if is_clash:
                                                                                break_value = 'g'
                                                                                is_break = True
                                                                                break
                                                                            
                                                                            return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d] + "," + sub_list[e] + "," + sub_list[f] + "," + sub_list[g] + "," + sub_list[h]
                                                                    else:
                                                                        for i in range(0, size):
                                                                            if is_break:
                                                                                if break_value == 'i': 
                                                                                    is_break = False
                                                                                else: break
                                                                            if size == 9:
                                                                                if(a != b and a != c and a != d and a != e and a != f and a != g and a != h and a != i and b != c  and b != d and b != e and b != f and b != g and b != h and b != i and c != d and c != e and c != f and c != g and c != h and c != i and d != e and d != f and d != g and d != h and d != i and e != f and e != g and e != h and e != i and f != g and f != h and f != i and g != h and g != i and h != i):
                                                                                    
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                                                    if is_clash:
                                                                                        break_value = 'a'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                                                    if is_clash:
                                                                                        break_value = 'b'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                                                    if is_clash:
                                                                                        break_value = 'c'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                                                    if is_clash:
                                                                                        break_value = 'd'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                                                    if is_clash:
                                                                                        break_value = 'e'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[f].split(":")[1], slot_list[5])
                                                                                    if is_clash:
                                                                                        break_value = 'f'
                                                                                        is_break = True
                                                                                        break
                                                                                                                                                        
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[g].split(":")[1], slot_list[6])
                                                                                    if is_clash:
                                                                                        break_value = 'g'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[h].split(":")[1], slot_list[7])
                                                                                    if is_clash:
                                                                                        break_value = 'h'
                                                                                        is_break = True
                                                                                        break
                                                                                    is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[i].split(":")[1], slot_list[8])
                                                                                    if is_clash:
                                                                                        break_value = 'h'
                                                                                        is_break = True
                                                                                        break
                                                                                    
                                                                                    return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d] + "," + sub_list[e] + "," + sub_list[f] + "," + sub_list[g] + "," + sub_list[h] + "," + sub_list[i]
                                                                            else:
                                                                                for j in range(0, size):
                                                                                    if size == 10:
                                                                                        if(a != b and a != c and a != d and a != e and a != f and a != g and a != h and a != i and a != j and b != c  and b != d and b != e and b != f and b != g and b != h and b != i and b != j and c != d and c != e and c != f and c != g and c != h and c != i and c != j and d != e and d != f and d != g and d != h and d != i and d != j and e != f and e != g and e != h and e != i and e != j and f != g and f != h and f != i and f != j and g != h and g != i and g != j and h != i and h != j and i != j):
                                                                                            
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[a].split(":")[1], slot_list[0])
                                                                                            if is_clash:
                                                                                                break_value = 'a'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[b].split(":")[1], slot_list[1])
                                                                                            if is_clash:
                                                                                                break_value = 'b'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[c].split(":")[1], slot_list[2])
                                                                                            if is_clash:
                                                                                                break_value = 'c'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[d].split(":")[1], slot_list[3])
                                                                                            if is_clash:
                                                                                                break_value = 'd'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[e].split(":")[1], slot_list[4])
                                                                                            if is_clash:
                                                                                                break_value = 'e'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[f].split(":")[1], slot_list[5])
                                                                                            if is_clash:
                                                                                                break_value = 'f'
                                                                                                is_break = True
                                                                                                break
                                                                                                                                                                
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[g].split(":")[1], slot_list[6])
                                                                                            if is_clash:
                                                                                                break_value = 'g'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[h].split(":")[1], slot_list[7])
                                                                                            if is_clash:
                                                                                                break_value = 'h'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[i].split(":")[1], slot_list[8])
                                                                                            if is_clash:
                                                                                                break_value = 'i'
                                                                                                is_break = True
                                                                                                break
                                                                                            is_clash = self.pool.get('sms.timetable.lines').check_clash(cr,uid,sub_list[j].split(":")[1], slot_list[9])
                                                                                            if is_clash:
                                                                                                break_value = 'i'
                                                                                                is_break = True
                                                                                                break

                                                                                            return sub_list[a] + "," + sub_list[b] + "," + sub_list[c] + "," + sub_list[d] + ":" + sub_list[e] + "," + sub_list[f] + "," + sub_list[g] + "," + sub_list[h] + "," + sub_list[i] + "," + sub_list[j]
    
    def close_class(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'Complete'})
        return True  
    
class sms_academiccalendar_student(osv.osv):
    """This object registers a student within a class in a session """
    
    def enroll_student_in_class(self, cr, uid, ids,fs, fee_start_month,class_of_admin,enrolment_type):
            
        print "student",ids
        print "fs",fs
        print "start m",fee_start_month
        print "class of admission",class_of_admin

        #step1: Register student to class
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,class_of_admin)
        std_cal_id = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                'name':class_of_admin,
                'date_enrolled':datetime.date.today(),
                'enrolled_by':uid,                                              
                'std_id':ids,
                'date_registered':datetime.date.today(),
                'state':'Current' })
        
        if std_cal_id:
                # srep3:Add subjects to student
                acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',class_of_admin),('state','!=','Complete')])
                for sub in acad_subs:
                    add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                    'student': std_cal_id,
                    'student_id': ids,
                    'subject': sub,
                    'subject_status': 'Current'})
                    
                #step3: Set Admission No
                admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,std_cal_id,acad_cal_obj.id)
                print "new admin no is ",admn_no
                
                self.pool.get('sms.student').write(cr, uid, ids, {'fee_starting_month':fee_start_month,'fee_type':fs, 'state': 'Admitted', 'current_state': 'Current','admitted_to_class':class_of_admin,'admitted_on':datetime.date.today(),'current_class':class_of_admin})
                cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,class_of_admin)
                
                if enrolment_type == 'new_admission':
                     
                     sqlfee1 =  """SELECT smsfee_classes_fees.id,smsfee_feetypes.id,smsfee_feetypes.subtype
                                FROM smsfee_classes_fees
                                INNER JOIN smsfee_feetypes
                                ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                WHERE smsfee_classes_fees.academic_cal_id ="""+str(class_of_admin)+"""
                                AND smsfee_classes_fees.fee_structure_id="""+str(fs)+"""
                                AND smsfee_feetypes.subtype IN('at_admission','Monthly_Fee','Annual_fee')
                                """
                else:
                    sqlfee1 =  """SELECT smsfee_classes_fees.id,smsfee_feetypes.id,smsfee_feetypes.subtype
                                FROM smsfee_classes_fees
                                INNER JOIN smsfee_feetypes
                                ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                WHERE smsfee_classes_fees.academic_cal_id ="""+str(class_of_admin)+"""
                                AND smsfee_classes_fees.fee_structure_id="""+str(fs)+"""
                                AND smsfee_feetypes.subtype IN('Promotion_Fee','Monthly_Fee','Annual_fee')
                                """
                
                
                
                cr.execute(sqlfee1)
                fees_ids = cr.fetchall() 
                print "this class fees,fees_ids",fees_ids   
                if fees_ids:
                    late_fee = 0
                    fee_month = ''
                    for idds in fees_ids:
                        print "generic fee_type ",fs
                        obj = self.pool.get('smsfee.classes.fees').browse(cr,uid,idds[0])
                        if idds[2] == 'Monthly_Fee':
                            print "calling method"
                            insert_monthly_fee = self.pool.get('smsfee.studentfee').insert_student_monthly_fee(cr,uid,ids,std_cal_id,class_of_admin,fee_start_month,idds[0])
                        else:
                            print "executing else"  
                            crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                            'student_id': ids,
                            'acad_cal_id': class_of_admin,
                            'acad_cal_std_id': std_cal_id,
                            'fee_type': obj.id,
                            'generic_fee_type':idds[1],
                            'date_fee_charged':datetime.date.today(),
                            'due_month': fee_start_month,
                            'fee_amount': obj.amount,
                            'paid_amount':0,
                            'late_fee':0,
                            'total_amount':obj.amount + late_fee,
                            'reconcile':False,
                            'state':'fee_unpaid'
                            })
                    else:
                          msg = 'Fee May be defined but not set for New Class:'       
#              
        
        return True  
    
    
    
    
    def _set_admission_no(self, cr, uid, ids,acad_cal_id):
        
        rec = self.pool.get('sms.academiccalendar.student').browse(cr,uid,ids)
        acad_cal = acad_cal_id
        cls_cat = rec.name.class_id.category
        session_id = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal).session_id.id
        start_date =  self.pool.get('sms.session').browse(cr,uid,session_id).start_date
        
        year = int(datetime.datetime.strptime(str(start_date), '%Y-%m-%d').strftime('%Y'))
             
        
        registration_ids = self.pool.get('sms.registration.format').search(cr,uid,[('state','=',True)])
        if registration_ids:
            
            reg_obj = self.pool.get('sms.registration.format').browse(cr,uid,registration_ids[0])
            cls_cat_sql = ""
            session_sql = ""
            if reg_obj.first == 'Category' or reg_obj.second == 'Category' or reg_obj.third == 'Category' or reg_obj.fourth == 'Category':
                cls_cat_sql = " AND sms_classes.category = '" + str(cls_cat) + "'"
            if reg_obj.counter_reset:
                session_sql = " AND sms_academiccalendar.session_id = """ + str(session_id)
            
            sql = """SELECT MAX(registration_counter) FROM sms_student
                INNER JOIN sms_academiccalendar
                ON sms_student.admitted_to_class = sms_academiccalendar.id
                INNER JOIN sms_classes
                ON sms_academiccalendar.class_id = sms_classes.id 
                WHERE sms_student.state != 'Draft'""" + cls_cat_sql + session_sql            
            cr.execute(sql)
            
            rows= cr.fetchone()
            if rows:
                if rows[0]==None:
                    count = 0
                else:
                    count = rows[0]
                new_stds = int(count) + 1 
                month = datetime.date.today().strftime("%m")
                
                if reg_obj.first == 'Category':
                    admin_no = str(cls_cat[:1])
                elif reg_obj.first == 'Year':
                   admin_no = str(year)
                elif reg_obj.first == 'Month':
                   admin_no = str(month)
                elif reg_obj.first == 'Counter': 
                    admin_no = str(new_stds)
                
                if reg_obj.second == 'Category':
                    admin_no = admin_no +  reg_obj.separator_1 + str(cls_cat[:1])
                elif reg_obj.second == 'Year':
                   admin_no = admin_no +  reg_obj.separator_1 + str(year)
                elif reg_obj.second == 'Month':
                   admin_no = admin_no +  reg_obj.separator_1 + str(month)
                elif reg_obj.second == 'Counter':
                    admin_no = admin_no +  reg_obj.separator_1 + str(new_stds)
                
                if reg_obj.third == 'Category':
                    admin_no = admin_no + reg_obj.separator_2 + str(cls_cat[:1])
                elif reg_obj.third == 'Year':
                   admin_no = admin_no + reg_obj.separator_2 + str(year)
                elif reg_obj.third == 'Month':
                   admin_no = admin_no + reg_obj.separator_2 + str(month)
                elif reg_obj.third == 'Counter':
                    admin_no = admin_no + reg_obj.separator_2 + str(new_stds)
    
                if reg_obj.fourth == 'Category':
                    admin_no = admin_no + reg_obj.separator_3 + str(cls_cat[:1])
                elif reg_obj.fourth == 'Year':
                   admin_no = admin_no + reg_obj.separator_3 + str(year)
                elif reg_obj.fourth == 'Month':
                   admin_no = admin_no + reg_obj.separator_3 + str(month)
                elif reg_obj.fourth == 'Counter':
                    admin_no = admin_no + reg_obj.separator_3 + str(new_stds)
                print "new reg no,",admin_no
                return str(admin_no)
            else:
                raise osv.except_osv(('Format Missing'),('Please Define a Registration No Format for this institute'))
                return 
    
    _name = 'sms.academiccalendar.student'
    _description = "registers new student in new class.."
    _columns = {
        'name': fields.many2one('sms.academiccalendar', 'Class',required=True),  
        'std_id': fields.many2one('sms.student', 'Student'),
        'std_reg_lineID': fields.one2many('sms.student.subject', 'student'),
        'class_att_ids':fields.one2many('sms.attendancelines','student_class','Attendance'),
        'marks_per': fields.float('Marks %'),
        'date_enrolled':fields.date('Date Enrolled'),
        'date_section_changed':fields.date('Date Section Changed'),
        'enrolled_by': fields.many2one('res.users', 'Enrolled By'),
        'section_changed_by': fields.many2one('res.users', 'Section Changed By'),
        'attendance_per': fields.float('Attendance %'),
        'latest_fee_month':fields.related('name','fee_update_till',type='many2one',relation='sms.session.months', string='Fee Register', readonly=True),
        'state': fields.selection([('Suspended','Suspended'),('Withdraw','Withdraw'),('Current', 'Current'),('Promoted', 'Promoted'),('Demoted', 'Demoted'),
                                   ('Conditionally_Promoted', 'Conditionally Promoted'),('Failed', 'Failed'),('section_changed', 'Section Changed')], 'States', readonly = True),
        'date_registered':fields.date('Date Registered'),
    } 
     
    _defaults = {
        'state': 'Current',
    }
    _sql_constraints = [('name_unique', 'unique (name,std_id,state)', """Student is already registered in selected class. """)]      
    
class sms_academiccalendar_subjects(osv.osv):
    """Stores new subjects in newly defined session.add subjects to class"""
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            subject_name = str(f.subject_id.name).replace(" ","")
            
            if f.offered_as == 'practical':
                #r_sub =  str(subject_name) + " ( " + str(f.reference_practical_of.subject_id.name).replace(" ","") + ")"
                if f.reference_practical_of.subject_id:
                    r_sub =  str(subject_name) + " ("+str(f.reference_practical_of.subject_id.name)+")"
                else:
                    r_sub =  str(subject_name) + " (???)"
                result[f.id] = r_sub 
            else:    
                result[f.id] = str(f.subject_id.name) 
        return result

    def unlink(self, cr, uid, ids, context={}, check=True):
        print "@@@@acd_cal_sub@@@@@",ids,context
        
        #-------------------------------------------------
        rec = self.browse(cr ,uid ,ids)[0]
        check_delete = rec.allow_delete
        if check_delete == True :
            acad_cal_id = rec.academic_calendar.id
            
            dsheet_id = self.pool.get('sms.exam.datesheet').search(cr,uid,[('academiccalendar','=',acad_cal_id),('status','=','Active')])
            acd_cal_stu_ids =  self.pool.get('sms.academiccalendar.student').search(cr ,uid ,[('name','=',acad_cal_id),('state','=','Current')])
            tota_stu = len(acd_cal_stu_ids)
    
            if  dsheet_id:
    
                subj_datesheet =  self.pool.get('sms.exam.datesheet.lines').search(cr,uid,[('name','in',dsheet_id),('subject','=',ids)])
                self.pool.get('sms.exam.datesheet.lines').unlink(cr ,uid ,subj_datesheet)
                
    
                if acd_cal_stu_ids :
                    stud_subj_id = self.pool.get('sms.student.subject').search(cr ,uid ,[('student','=',acd_cal_stu_ids),('subject','=',ids)])
                if stud_subj_id:
                    rec_stud_subj = self.pool.get('sms.student.subject').browse(cr ,uid ,stud_subj_id)
                     
                    
                    
                    for acd_stu in rec_stud_subj:
                        self.pool.get('sms.student.subject').unlink(cr ,uid ,acd_stu.id)
                    
                for rec in self.browse(cr, uid, ids, context):
                    super(osv.osv, self).unlink(cr, uid, ids, context)            
                        
                    
           # raise osv.except_osv(('SSSTTTOOOPPP'),('........'))
        else:
             raise osv.except_osv(('Subject Remission Denied'),('This subject that you are trying to remove is assigned to students first check the allow delete checkbox of subject '))
        return None
            
    def create(self, cr, uid, vals, context=None, check=True):
        
        exm_id = ""
        #create this new subject
        new_subject = super(osv.osv, self).create(cr, uid, vals, context)
        #now check if exams is started in active state for class of this subject, then add this subject 
        #firt get class id from this subject parent and search that class in active exams
        
        rec = self.browse(cr,uid,new_subject)
        acad_cal_id = rec.academic_calendar.id
        
        #search this class in active exams, if this class is in active exams, it means its exams are running 
        # this newly added subject will also be added to exams
    
        dsheet_id = self.pool.get('sms.exam.datesheet').search(cr,uid,[('academiccalendar','=',acad_cal_id),('status','=','Active')])
        if dsheet_id:
            add_subject = self.pool.get('sms.exam.datesheet.lines').create(cr,uid,{
                           'name': dsheet_id[0],
                           'subject': new_subject,
                           'total_marks': 0
                           })

         #-----------assign subj to students of this class------------------------------     
        #first find acad cal student ids of all student
        acd_cal_stu_ids =  self.pool.get('sms.academiccalendar.student').search(cr ,uid ,[('name','=',acad_cal_id),('state','=','Current')])
        
        if acd_cal_stu_ids :
            rec_cal_std = self.pool.get('sms.academiccalendar.student').browse(cr ,uid ,acd_cal_stu_ids) 
        
        for acd_stu in rec_cal_std:
            stu_sub_id = self.pool.get('sms.student.subject').create(cr ,uid ,{
                      'student': acd_stu.id ,
                      'student_id':acd_stu.std_id.id ,
                      'subject': new_subject ,
                      'subject_status': 'Current'
                      })
    
            # use this portio onward if student fee is to be added on subject registration, call a method that adds fee to student
        return new_subject
    
    
    _name = 'sms.academiccalendar.subjects'
    _description = "Defines subjects for new class in session."
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Subject',type='char'),
        'subject_id': fields.many2one('sms.subject', 'Subject',required=True),  
        'academic_calendar': fields.many2one('sms.academiccalendar','Class'),
        'total_marks': fields.float('Total Marks(%)'),
        'passing_marks': fields.float('Passing marks(%)'),
        'min_require_att': fields.float('Attendance Per'),
        'state': fields.selection([('Draft','Draft'),('Current', 'Current'),('Closed', 'Closed')], 'States'),
        'teacher_id': fields.many2one('hr.employee','Teacher'),
        'offered_as': fields.selection([('theory','Theory Only'),('theory_practical','Theory + Practical'),('practical','Practical Only')], 'Offered As'),
        'reference_practical_of': fields.many2one('sms.academiccalendar.subjects', 'Main Subject',),
        'allow_delete' : fields.boolean('Allow Deletion')
    }
     
    _defaults = {
        'state': 'Draft',
        'allow_delete' : False,
    }
    _sql_constraints = [('name_unique', 'unique (subject_id,academic_calendar)', """Subject Already Added to Class. """)]     
    

class sms_student_subject(osv.osv):
    """Stores students subjects in new class"""
    
    
    
    def _set_subj_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = str(f.subject.name)  
          
        return result
    
    _name = 'sms.student.subject'
    _description = "Defines subjects for new class in session."
    _columns = {
        'name':fields.function(_set_subj_name, method=True,  string='Subject',type='char'),
        'student': fields.many2one('sms.academiccalendar.student', 'Student'),
        'student_id':fields.many2one('sms.student','StudentID'),
        'subject': fields.many2one('sms.academiccalendar.subjects', 'Subject', required=True),
        'subject_status': fields.selection([
            ('Current','Current'),
            ('Pass','Pass'),
            ('Withdraw','Withdraw'),
            ('Fail','Fail'),
            ('Suspended','Suspended')]),
        'classes_taken': fields.integer('Classes Taken',readonly=True),
        'classes_attended': fields.integer('Classes Attended',readonly=True), 
        'current_agrt': fields.float('Attendance(%)',readonly=True),
        'obtained_percentage': fields.float('Obtained Percentage', readonly=True),
        'subject_marks': fields.float('Subject Marks', readonly=True),
        'subject_grade': fields.char('Subject Grade', size=150, readonly=True),
        'subject_remarks': fields.char('Subject Remarks', size=150, readonly=True),
        'subject_exams_result':fields.one2many('sms.exam.lines','student_subject','Results'),
        'reference_practical_of': fields.many2one('sms.student.subject', 'Practical Of'),
        
#         'student_subject_attendance': fields.one2many('sms.attendancelines','subject','Subjects Attendence'),
#         'student_subject_marks': fields.one2many('sms.exame','subject','Subjects Marks'),
    }
    _defaults = {
        'subject_status':'Current',
        
        
        
    }
    _sql_constraints = [  
        ('semester_subject', 'unique (student,subject,subject_status)', 'Student Already Registered with subject !')
    ]     

###   Default Data Setting   ###
class sms_academiccalendar_default(osv.osv):
    """Stores academic calendar default data """

    _name = 'sms.academiccalendar.default'
    _columns = {
        'name': fields.many2one('sms.classes', 'Class', ondelete='cascade'),
        'admission_fee': fields.integer('Admission Fee'),
        'monthly_fee': fields.integer('Monthly Fee'),
        'annual_fee': fields.integer('Annual Fee'),
        'library_fee': fields.integer('Library Fee'),
        'partial_admission_fee': fields.integer('Admission Fee'),
        'partial_monthly_fee': fields.integer('Monthly Fee'),
        'partial_annual_fee': fields.integer('Annual Fee'),
        'partial_libraryfee': fields.integer('Library Fee'),
        'default_subjects_id': fields.one2many('sms.academiccalendar.subjects.default','academic_calendar', 'Subjects'),
    }
sms_academiccalendar_default()

class sms_academiccalendar_subjects_default(osv.osv):
    """This object is used to store the academic Calendar lines of defaultnstration data"""
    
    _name = 'sms.academiccalendar.subjects.default'
    _columns = {
        'name': fields.many2one('sms.subject', 'Subject', required=True),
        'academic_calendar': fields.many2one('sms.academiccalendar.default', 'Class', ondelete='cascade'),
        'no_of_classes': fields.integer('No Of Classes', required=True),
        'lab_required': fields.boolean('Lab Required '),
    }
    _defaults = {
        'lab_required':False,}
        
sms_academiccalendar_subjects_default()

class sms_time(osv.osv):
    
    """ This object defines Time for class of an institute """
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            hour = f.hour
            mint = f.minute
            if hour < 10:
                hour = "0" + str(hour)
            if mint < 10:
                mint = "0" + str(mint)
            result[f.id] = str(hour) + ":" + str(mint) + " " + (f.am_pm)
        return result
    
    def _set_name_24(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            hour = f.hour_24
            mint = f.minute
            if hour < 10:
                hour = "0" + str(hour)
            if mint < 10:
                mint = "0" + str(mint)
            result[f.id] = str(hour) + ":" + str(mint)
        return result
    
    def _set_hour_24(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.hour
            
            if f.am_pm == "PM":
                if f.hour != 12: 
                    result[f.id] = f.hour + 12
        return result

    _name = 'sms.time'
    _description = "This object store time for classes"
    _columns = {
        'name':fields.function(_set_name, method=True, size=256, string='Name',type='char', store=True),
        'hour_24': fields.function(_set_hour_24, method=True, string='Hour(24)',type='integer', store=True),
        'name_24':fields.function(_set_name_24, method=True, size=256, string='Name(24)',type='char', store=True),
        'hour': fields.integer('hours', required = True),
        'minute': fields.integer('minutes', required = True),
        'am_pm': fields.selection([('AM', 'AM'),('PM', 'PM')], 'AM/PM', required = True),
    }
    
    defaults = {
                'am_pm':'AM'
       }
sms_time()

class sms_timetable_slot(osv.osv):
    
    """ This object defines Timetable Slot for class of an institute """
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = str(f.start_time.name) + " -- " + str(f.end_time.name) 
        return result
    
    def _set_start_24time(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.start_time.hour_24
        return result
    
    def _set_end_24time(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.end_time.hour_24
        return result
    
    def _set_name_24(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = str(f.start_time.name_24) + " -- " + str(f.end_time.name_24) 
        return result
    
    _name = 'sms.timetable.slot'
    _description = "This object store timetable for classes"
    _columns = {
        'name':fields.function(_set_name, method=True, size=256, string='Name',type='char', store=True),
        'start_time': fields.many2one('sms.time', 'Start Time', required = True),
        'end_time': fields.many2one('sms.time', 'End Time', required = True),
        'name_24':fields.function(_set_name_24, method=True, size=256, string='Name(24)',type='char', store=True),
        'start_24_time': fields.function(_set_start_24time, method=True, string='Start Time(24)',type='integer', store=True),
        'end_24_time': fields.function(_set_end_24time, method=True, string='End Time(24)',type='integer', store=True),

    } 
    
    _order = "name"
    
    defaults = {
    }
sms_timetable_slot()


class sms_day(osv.osv):
    
    """ This object defines Days of week of an institute """
    
    _name = 'sms.day'
    _description = "This object store timetable for classes"
    _columns = {
        'name': fields.char('Name', size=200, required = True),
#         'name': fields.selection([('1 Monday', 'Monday'),('2 Tuesday', 'Tuesday'),('3 Wednesday', 'Wednesday'),
#                                   ('4 Thursday', 'Thursday'),('5 Friday', 'Friday'),('6 Saturday', 'Saturday')
#                                   ('7 Sunday', 'Sunday')], 'Status', required = True),
#         
        'active': fields.boolean('Active'),    
    } 
    
    defaults = {
    }
sms_day()

class sms_timetable(osv.osv):
    
    """ This object defines Timetable for class of an institute """
     
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = "Timetable For " + str(f.academic_id.name)
        return result
    
    _name = 'sms.timetable'
    _description = "This object store timetable for classes"
    _columns = {
        'name':fields.function(_set_name, method=True, size=256, string='Name',type='char', store=True),
        'state': fields.selection([('Draft', 'Draft'),('Active', 'Active'),('Inactive', 'Inactive')], 'Status', required = True),
        'start_date': fields.date("Start",required=True) ,
        'end_date': fields.date("End",required=True),
        'academic_id': fields.many2one('sms.academiccalendar','Academic Calendar', required = True),
        'timetable_lines':fields.one2many('sms.timetable.lines','timetable_id','Timetable Lines', required = True),
    } 
    
    defaults = {
        'state': 'Draft',
    }
sms_timetable()

class sms_timetable_lines(osv.osv):
    
    """ This object defines Timetable Lines for class of an institute """
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            teacher = str(f.teacher_id.name)
            subject = str(f.subject_id.name)
            
            if f.type == 'Break':
                result[f.id] = str(f.type) + " " + str(f.period_break_no)
            else:
                result[f.id] = str(f.type) + " " + str(f.period_break_no) + " (" + teacher + "  - " +  subject + ")"
        return result
	
	
    def check_clash (self, cr, uid, teacher_id, slot_name, context=None):
        teacher_id = int(teacher_id)
        
        # "09:15 AM -- 09:45 AM"
        slot_start_time = 0
        slot_end_time = 0
        asigned_start_time = 0
        asigned_end_time = 0
        
        start = slot_name.split("--")[0].strip()
        end = slot_name.split("--")[1].strip()
        
        slot_start_time_hour = int(start.split(" ")[0].split(":")[0])
        slot_start_time_min = int(start.split(" ")[0].split(":")[1])
        slot_start_time_am_pm = start.split(" ")[1]
        
        if slot_start_time_am_pm == 'PM' and slot_start_time_hour != 12:
            slot_start_time_hour = slot_start_time_hour + 12
        slot_start_time =  slot_start_time_hour * 60 + slot_start_time_min
        
        slot_end_time_hour = int(end.split(" ")[0].split(":")[0])
        slot_end_time_min = int(end.split(" ")[0].split(":")[1])
        slot_end_time_am_pm = end.split(" ")[1]
        
        if slot_end_time_am_pm == 'PM' and slot_end_time_hour != 12:
            slot_end_time_hour = slot_end_time_hour + 12
        slot_end_time =  slot_end_time_hour * 60 + slot_end_time_min

        timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id)])
        print "iidddsss", timetable_lines_ids
        timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
        print "objjjjcs", timetable_lines_objs
        for rec in timetable_lines_objs:
            start_time_hour = rec.timetable_slot_id.start_time.hour
            start_time_min = rec.timetable_slot_id.start_time.minute
            
            if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
                start_time_hour = start_time_hour + 12
                
            end_time_hour = rec.timetable_slot_id.end_time.hour
            end_time_min = rec.timetable_slot_id.end_time.minute
            
            if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
                end_time_hour = end_time_hour + 12
            
            asigned_start_time = start_time_hour * 60 + start_time_min
            asigned_end_time = end_time_hour * 60 + end_time_min
      
            if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
                return True
            elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
                return True
                                
        return False
   
    def onchange_teacher_id(self, cr, uid, ids, teacher_id, day_id, context=None):
        slot_ids = []
        query = """SELECT sms_timetable_slot.name, start_time, end_time , id
            from sms_timetable_slot order by name"""
        cr.execute(query)
        slot_records = cr.fetchall()
        # "09:15 AM -- 09:45 AM"
        for slot in slot_records:
            slot_start_time = 0
            slot_end_time = 0
            asigned_start_time = 0
            asigned_end_time = 0
            
            start = slot[0].split("--")[0].strip()
            end = slot[0].split("--")[1].strip()
            
            slot_start_time_hour = int(start.split(" ")[0].split(":")[0])
            slot_start_time_min = int(start.split(" ")[0].split(":")[1])
            slot_start_time_am_pm = start.split(" ")[1]
            
            if slot_start_time_am_pm == 'PM' and slot_start_time_hour != 12:
                slot_start_time_hour = slot_start_time_hour + 12
            slot_start_time =  slot_start_time_hour * 60 + slot_start_time_min
            
            slot_end_time_hour = int(end.split(" ")[0].split(":")[0])
            slot_end_time_min = int(end.split(" ")[0].split(":")[1])
            slot_end_time_am_pm = end.split(" ")[1]
            
            if slot_end_time_am_pm == 'PM' and slot_end_time_hour != 12:
                slot_end_time_hour = slot_end_time_hour + 12
            
            slot_end_time =  slot_end_time_hour * 60 + slot_end_time_min

            timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id)])
            timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
            
            for rec in timetable_lines_objs:
                start_time_hour = rec.timetable_slot_id.start_time.hour
                start_time_min = rec.timetable_slot_id.start_time.minute
                
                if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
                    start_time_hour = start_time_hour + 12
                    
                end_time_hour = rec.timetable_slot_id.end_time.hour
                end_time_min = rec.timetable_slot_id.end_time.minute
                
                if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
                    end_time_hour = end_time_hour + 12
                
                asigned_start_time = start_time_hour * 60 + start_time_min
                asigned_end_time = end_time_hour * 60 + end_time_min
        
                if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
                    slot_ids.append(slot[3])
                elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
                    slot_ids.append(slot[3])

#             timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('day_id','=',day_id)])
#             timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
#             
#             for rec in timetable_lines_objs:
#                 start_time_hour = rec.timetable_slot_id.start_time.hour
#                 start_time_min = rec.timetable_slot_id.start_time.minute
#                 
#                 if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
#                     start_time_hour = start_time_hour + 12
#                     
#                 end_time_hour = rec.timetable_slot_id.end_time.hour
#                 end_time_min = rec.timetable_slot_id.end_time.minute
#                 
#                 if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
#                     end_time_hour = end_time_hour + 12
#                 
#                 asigned_start_time = start_time_hour * 60 + start_time_min
#                 asigned_end_time = end_time_hour * 60 + end_time_min
#         
#                 if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
#                     slot_ids.append(slot[3])
#                 elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
#                     slot_ids.append(slot[3])
            
        slot_ids = []        
        return {'domain':{'timetable_slot_id':[('id','not in',slot_ids)]}}

    def onchange_day_id(self, cr, uid, ids, teacher_id, day_id, context=None):
        slot_ids = []
        query = """SELECT sms_timetable_slot.name, start_time, end_time , id
            from sms_timetable_slot order by name"""
        cr.execute(query)
        slot_records = cr.fetchall()
        # "09:15 AM -- 09:45 AM"
        for slot in slot_records:
            slot_start_time = 0
            slot_end_time = 0
            asigned_start_time = 0
            asigned_end_time = 0
            
            start = slot[0].split("--")[0].strip()
            end = slot[0].split("--")[1].strip()
            
            slot_start_time_hour = int(start.split(" ")[0].split(":")[0])
            slot_start_time_min = int(start.split(" ")[0].split(":")[1])
            slot_start_time_am_pm = start.split(" ")[1]
            
            if slot_start_time_am_pm == 'PM' and slot_start_time_hour != 12:
                slot_start_time_hour = slot_start_time_hour + 12
            slot_start_time =  slot_start_time_hour * 60 + slot_start_time_min
            
            slot_end_time_hour = int(end.split(" ")[0].split(":")[0])
            slot_end_time_min = int(end.split(" ")[0].split(":")[1])
            slot_end_time_am_pm = end.split(" ")[1]
            
            if slot_end_time_am_pm == 'PM' and slot_end_time_hour != 12:
                slot_end_time_hour = slot_end_time_hour + 12
            
            slot_end_time =  slot_end_time_hour * 60 + slot_end_time_min

#             timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id),('day_id','=',day_id)])
#             timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
            timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id)])
            timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
            
            for rec in timetable_lines_objs:
                start_time_hour = rec.timetable_slot_id.start_time.hour
                start_time_min = rec.timetable_slot_id.start_time.minute
                
                if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
                    start_time_hour = start_time_hour + 12
                    
                end_time_hour = rec.timetable_slot_id.end_time.hour
                end_time_min = rec.timetable_slot_id.end_time.minute
                
                if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
                    end_time_hour = end_time_hour + 12
                
                asigned_start_time = start_time_hour * 60 + start_time_min
                asigned_end_time = end_time_hour * 60 + end_time_min
        
                if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
                    slot_ids.append(slot[3])
                elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
                    slot_ids.append(slot[3])

            timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('day_id','=',day_id)])
            timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
            
            for rec in timetable_lines_objs:
                start_time_hour = rec.timetable_slot_id.start_time.hour
                start_time_min = rec.timetable_slot_id.start_time.minute
                
                if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
                    start_time_hour = start_time_hour + 12
                    
                end_time_hour = rec.timetable_slot_id.end_time.hour
                end_time_min = rec.timetable_slot_id.end_time.minute
                
                if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
                    end_time_hour = end_time_hour + 12
                
                asigned_start_time = start_time_hour * 60 + start_time_min
                asigned_end_time = end_time_hour * 60 + end_time_min
        
                if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
                    slot_ids.append(slot[3])
                elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
                    slot_ids.append(slot[3])
            
        return {'domain':{'timetable_slot_id':[('id','not in',slot_ids)]}}
    
    def onchange_type(self, cr, uid, ids, type, context=None):
        result = {}
        if type == 'Break':
            result['teacher_id'] = ''
            result['subject_id'] = ''
            return {'value': result}
        return {}
    
    def _set_slot_name_24(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
           result[f.id] = f.timetable_slot_id.name_24
        return result
    
    _name = 'sms.timetable.lines'
    _description = "This object store timetable for classes"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Name',type='char'),
        'period_break_no': fields.integer('Sequence No', required = True),
        'is_lab': fields.boolean('Is Lab'),    
        'type': fields.selection([('Period', 'Period'),('Break', 'Break')], 'Slot Type', required = True),
        #'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject'),
        'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('teacher_id','=',teacher_id),('teacher_id','!=',None)]]"),
        'teacher_id': fields.many2one('hr.employee','Teacher'),
        'day_id': fields.many2one('sms.day','Day', required = True),
        'timetable_slot_id': fields.many2one('sms.timetable.slot','Timing', required = True),
        'timetable_id': fields.many2one('sms.timetable','Timetable'),
        'slot_name_24':fields.function(_set_slot_name_24, method=True,  string='Name',type='char', store=True),
    }
    
    _order = "day_id, slot_name_24"
    
    _defaults = {  
             'type': 'Period',
        }
sms_timetable_lines()


###   Default Data Setting   ###
class sms_timetable_default(osv.osv):
    """Stores Timetable default data """

    _name = 'sms.timetable.default'
    _columns = {
        'name': fields.many2one('sms.classes', 'Class', ondelete='cascade'),
        'timetable_lines':fields.one2many('sms.timetable.lines.default','timetable_id','Timetable Lines', required = True),
    }
sms_timetable_default()

class sms_timetable_lines_default(osv.osv):
    """This object is used to store the Timetable Lines of default data"""
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = str(f.type) + " " + str(f.period_break_no) 
        return result
    
    _name = 'sms.timetable.lines.default'
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Name',type='char'),
        'period_break_no': fields.integer('Sequence No', required = True),
        'type': fields.selection([('Period', 'Period'),('Break', 'Break')], 'Slot Type', required = True),
        'timetable_slot_id': fields.many2one('sms.timetable.slot','Timing', required = True),
        'timetable_id': fields.many2one('sms.timetable.default','Timetable'),
    }
        
sms_timetable_lines_default()

class sms_feestructure(osv.osv):
    
    def create(self, cr, uid, vals, context=None, check=True):
        new_fs = super(osv.osv, self).create(cr, uid, vals, context)
        sql = """SELECT id,name FROM smsfee_feetypes"""
        cr.execute(sql)
        rows = cr.fetchall()
        if rows:
            sql = """SELECT DISTINCT sms_classes.id from sms_classes
                  INNER JOIN sms_academiccalendar ON sms_classes.id = sms_academiccalendar.class_id"""
            cr.execute(sql)
            classes = cr.fetchall()
            if classes:
                for class_id in classes:
                   for ft in rows:
                       create = self.pool.get('smsfee.generic.classes.fees').create(cr, uid, {
                               'sms_class_id': class_id,
                               'fee_structure_id':new_fs,
                               'fee_type_id': ft[0],
                               'amount': 0})   
                
        return new_fs
    
    
    
    """ all Structures """
    _name = 'sms.feestructure'
    _description = "This object store fee types"
    _columns = {
        'name': fields.char(string = 'Structure',size = 100,required = True),      
        'description': fields.char(string = 'description',size = 100),
        'helptxt': fields.text('Help Text',readonly = True),
        'classes_ids': fields.one2many('smsfee.generic.classes.fees', 'fee_structure_id', 'Classes'),
        'session': fields.many2one('sms.session','Session'),
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique(name)', 'Feestructure Already exists!')
    ] 
    _defaults = {
        'helptxt' :'\n\nA Student is Enrolled against a predefinced fee Structure.\n\n\t1: Normal Fee,\n\t2: Teacher Son,\n\t3: Sibling.\n\nStudents fees are chared addocring to the fee sructure they are enrolled.|n Define all fee strucures your institute is following.'
    }
sms_feestructure()


class sms_attendance(osv.osv):
    """This object is used to store inforamtion about taken classes by teachers on given dates, 
       """ 
    _name = 'sms.attendance'
    _columns = {
        'class': fields.many2one('sms.academiccalendar', 'Class'),
        'teacher':fields.selection([('Taken','Taken'),('Deleted','Deleted')]),#fields.many2one('hr.employee','Teacher')
        'cls_date': fields.date('Attendance Date'),
        'class_state':fields.selection([('Taken','Taken'),('Deleted','Deleted')]),
        'user_id':fields.many2one('res.users','Current User'),
        'entry_date': fields.date('Attendance Date'),        
    }
    _sql_constraints = [  
        ('Attendance Exists', 'unique (class,cls_date)', 'Attendance already Entered !')
    ]  
sms_attendance()

class sms_attendancelines(osv.osv):
    """This object is used to store inforamtion about taken classes by teachers on given dates, 
       """ 
    _name = 'sms.attendancelines'
    _columns = {
        'student_class': fields.many2one('sms.academiccalendar.student', 'Subject'),
        'class_id': fields.many2one('sms.academiccalendar', 'Class'),
        'cls_date': fields.date('Attendance Date',required=True),
        'attandence_status': fields.selection([
            ('Present','Present'),
            ('Leave','Leave'),
            ('Absent','Absent')],
        'Attendance Status', required=True),
        }
    _sql_constraints = [  
        ('Attendance Exists', 'unique (student_class,cls_date)', 'Attendance already Entered !')]  

sms_attendancelines()

class sms_exam_type(osv.osv):
    """This object is used to store generic exam types"""
    
    _name = 'sms.exam.type'
    _columns = {
        'name': fields.char('Exam Type', size=150, required=True),
        'sequence_no': fields.integer('Sequence No' , required=True),
    }
sms_exam_type()

class sms_exam(osv.osv):
    """This ."""
        
    _name = 'sms.exam'
    _columns = {
        'name': fields.many2one('sms.exam.datesheet', 'Exam Type'),
        'exam_lines' :fields.one2many('sms.exam.lines', 'parent_exam', 'Exams Lines'),         
        'entry_date': fields.date("Entry Date",required=True),
        'subject_id' :fields.many2one('sms.academiccalendar.subjects', 'Subject', required=True), 
    }       
sms_exam()


class sms_exam_lines(osv.osv):
    """This object is used to store student Exam Marks."""
        
    _name = 'sms.exam.lines'
    _columns = {
        'name': fields.many2one('sms.exam.datesheet', 'Exam Type', required=True),
        'student_subject': fields.many2one('sms.student.subject', 'Student Subject', required=True),
        'exam_status': fields.selection([('Present','Present'),('Absent','Absent'),('UFM','Unfair Means'),],'Exam Status', required=True),
        'obtained_marks': fields.float('Obtained Marks', required=True),
        'total_marks': fields.float('Total Marks', required=True),
        'parent_exam' :fields.many2one('sms.exam', 'Parent Exam', readonly=True),
    }       
sms_exam_lines()

class sms_exam_default(osv.osv):
    
    def _user_get(obj,cr,uid,context={}):
        return uid

    _name= "sms.exam.default"
    _descpription = "Parent Default Exam Table"
    _columns = { 
        'user_id': fields.many2one('res.users','Created By', required=True),        
        'exam_lines' :fields.one2many('sms.exam.default.lines', 'parent_default_exam', 'Exams Lines'),         
        'entry_date': fields.date("Entry Date",required=True),
        'subject_id' :fields.many2one('sms.academiccalendar.subjects', 'Subject', required=True),         
        }
    _defaults = {
        'user_id' : _user_get,
    }
sms_exam_default()
        
class sms_exam_default_lines(osv.osv):
    _name= "sms.exam.default.lines"
    _descpription = "Default Exam Lines"
    _columns = { 
        'name': fields.char('Student Name',size=256, readonly=True),
        'father_name': fields.char('Father Name',size=25, readonly=True),
        'registration_no': fields.char('Admission No',size=25, readonly=True),
        'exam_type': fields.many2one('sms.exam.datesheet', 'Exam Type',readonly=True),
        'exam_status': fields.selection([('Present','Present'),('Absent','Absent'),('UFM','Unfair Means'),],'Exam Status', required=True),
        'obtained_marks': fields.float('Obtained Marks', required=True),
        'total_marks': fields.float('Total Marks', required=True, readonly=True),
        'parent_default_exam' :fields.many2one('sms.exam.default', 'Parent Exam', readonly=True),
        'exam_id' :fields.many2one('sms.exam.lines', 'Exam ID', readonly=True),
        }
    
    _defaults = {
        'exam_status': lambda *a: 'Present',
        'obtained_marks': lambda *a: 0,
        'total_marks': lambda *a: 100,
    }
     
    def onchange_exam_status(self, cr, uid, ids, exam_status, context={}):
        
        if exam_status=='Absent' or exam_status=='UFM':
            vals = {}
             
            marks_rows = self.browse(cr, uid, ids, context=context)
            for marks_row in marks_rows:
                vals['obtained_marks'] = 0.0
                
#                 sql = "UPDATE sms_student_subject_exam SET obtain_marks = """ + str(value) + """, 
#                     exam_status= '""" + str(exam_status) + """' WHERE id = """ + str(ids[0])
#                 cr.execute(sql);
#                 cr.commit();
            
            return { 'value':vals }
        else:
            return {}
    
    def onchange_exam_marks(self, cr, uid, ids, exam_marks, examtype_id, context={}):
        if ids:
            vals = {}
            marks_rows = self.browse(cr, uid, ids, context=context)
            for marks_row in marks_rows:
                if exam_marks > marks_row.total_marks:
                    vals['obtained_marks'] = 0.00
                 
                if marks_row.exam_status=='Absent' or marks_row.exam_status=='UFM':
                    vals['obtained_marks'] = 0.00
                 
            return { 'value':vals  }
        else:
            return {}
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        
        default_details_obj = self.browse(cr, uid, ids, context=context)
        
        for obj in default_details_obj:
            
            self.pool.get('sms.exam.lines').write(cr, uid, [obj.exam_id.id], {
                    'exam_status':obj.exam_status,
                    'obtained_marks':obj.obtained_marks,
                    'total_marks':obj.total_marks,
                    })
        
        return True
     
#     def unlink(self, cr, uid, ids, context=None):
#         obj =  self.browse(cr, uid, ids, context=context)
#         if obj[0].exam_id:
#             for each in obj:
#                 if each.student_subject_status == 'Current':
#                     self.pool.get('sms.exame').unlink(cr, uid, [each.exam_id],context)
#                 else:
#                     self.pool.get('sms.reappear.exame').unlink(cr, uid, [each.exam_id],context)
#         super(osv.osv, self).unlink(cr, uid, ids, context)
#         return True
sms_exam_default_lines()

class sms_exam_offered(osv.osv):
    _name= "sms.exam.offered"
    _descpription = "Stores exam offered"
    
    def onchange_exam_start_date(self, cr, uid, ids,start_date):
        result = {}
        value = ''
        sdate = start_date.split('-')
        session_year = self.pool.get('sms.session.months')._get_session_month_from_calendar_month(cr,uid,sdate[0],sdate[1])
        result['session_year'] = session_year[0]['session']
        return {'value':result}
           
    
    def set_exam_offered_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            exam_name = obj.exam_type.name
            sdate = obj.start_date.split('-')
            monthyear = str(self.pool.get('sms.exam.datesheet').get_month(cr, int(sdate[1]))) + ', ' + str(sdate[0])
            result[obj.id] =  exam_name + ": " + str(monthyear)
        return result
    
    def set_result(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] =  70.6
        return result
    
    def start_exam(self, cr, uid, ids, *args):
        rec = self.browse(cr,uid,ids)
        print "exam offered id",rec[0].id
        # find active academiccalendars that of this session
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr,uid,[('state','=','Active'),('session_id','=',rec[0].session_year.id)])
        if academiccalendar_ids:
            self.write(cr, uid, ids, {'state':'Active','start_date':datetime.date.today()})
            for calendar in academiccalendar_ids:
                datesheet_id = self.pool.get('sms.exam.datesheet').create(cr,uid,{
                                                            'academiccalendar':calendar, 
                                                            'exam_type':rec[0].exam_type.id,
                                                            'exam_offered':rec[0].id,
                                                            'start_date':rec[0].start_date,
                                                            'status':'Active'})
        else:
            raise osv.except_osv(('Cannot Start Exam'),('No Active class found for this exam, You have either all clesses in Draft State,OR you didnot create classes for this session'))
        return True
    
    def close_exam(self, cr, uid, ids, *args):
        
        rec = self.browse(cr,uid,ids)
        #1.find all classes in this exam to close
        
        datesheet_ids = self.pool.get('sms.exam.datesheet').search(cr,uid,[('status','=','Active'),('exam_offered','=',rec[0].id)])
        
        if datesheet_ids:
            rec_datesheet = self.pool.get('sms.exam.datesheet').browse(cr,uid,datesheet_ids)
            
            #2. Search all subjects in these classes
            for ds in rec_datesheet:
                #3. Search subjects in date sheet and close it
                datesheetlines_ids = self.pool.get('sms.exam.datesheet.lines').search(cr,uid,[('open_for_edit','=',True),('name','=',ds.id)])
                
                if datesheetlines_ids:
                    #close all subjects
                    for subject in datesheetlines_ids:
                        close_subject = self.pool.get('sms.exam.datesheet.lines').close_exam_subject(cr,uid,subject)
                        
                #4 close all classes in tis exam
                close_classes_exam = self.pool.get('sms.exam.datesheet').close_exam_class(cr,uid,ds.id)
        #5 close offered exam
        self.write(cr, uid, ids, {'state':'Closed','start_date':datetime.date.today()})
        return True
    
    def cancel_exam(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'Draft','closing_date':datetime.date.today()})
        return True
    
    _columns = { 
        'name':fields.function(set_exam_offered_name, method=True,  string='Exam Offered',type='char', store=True),
        'exam_type': fields.many2one('sms.exam.type', 'Exam Type',required=True),
        'start_date': fields.date('Start Date',required =True),
        'closing_date': fields.date('Closing Date'),
        'session_year': fields.many2one('sms.session', 'Session',  required=True, help="Session Year "),
        'state': fields.selection([('Draft','Draft'),('Active','Active'),('Closed','Closed'),('Cancelled','Cancelled')],'Status'),
        'datesheet_ids' :fields.one2many('sms.exam.datesheet', 'exam_offered', 'Datesheets'),
        'result':fields.function(set_result, method=True,  string='Result(%)',type='float'),
        }
    
    _defaults = {
        'state': lambda *a: 'Draft',
        }
    
class sms_exam_datesheet(osv.osv):
    
    """This object register academic calender in to active exams, when click on start exams all acitve
       academic calenders are registered in this object.appeared as one2many to sms.exam.offered """
    _name= "sms.exam.datesheet"
    _descpription = "Stores exam date sheets"
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = {}
        class_exam_id = super(osv.osv, self).create(cr, uid, vals, context)
        rec = self.browse(cr,uid,class_exam_id)
        subjects = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',rec.academiccalendar.id),('state','=','Current')])
        if subjects:
            for sub in subjects:
                add_subjects = self.pool.get('sms.exam.datesheet.lines').create(cr,uid,{
                        'name':class_exam_id,                                                       
                        'subject':sub,
                        'paper_date':datetime.date.today(), 
                        'invigilator':uid, 
                        'total_marks':0 })
                                 
        return
    
    def set_datesheet(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            exam_name = obj.exam_offered.exam_type.name
            sdate = obj.exam_offered.start_date.split('-')
            monthyear = str(self.get_month(cr, int(sdate[1]))) + ', ' + str(sdate[0])
            result[obj.id] =  exam_name + ": " + str(monthyear) 
        return result
   
    def set_result(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = ''
        return result
    
    def _get_exam_type(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] =  obj.exam_offered.exam_type.id
        return result
    
    def _get_exam_date(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] =  obj.exam_offered.start_date
        return result
    
    def close_exam_class(self, cr, uid, ds_id):
        """This method will do three things 
           it will cancel exams when called with cancel exam button
           it will close exam when called with close exam button on this object
           it will close and cancel exams on parent exams called when they are closed or canceled"""
        self.write(cr,uid,ds_id,{'status':'Closed'})
        return 
    
    _columns = { 
        'name':fields.function(set_datesheet, method=True,  string='Exam',type='char', store=True),
        'exam_type':fields.function(_get_exam_type, string='Exam Type', type='many2one', relation="sms.exam.type", store=True),
        'academiccalendar':fields.many2one('sms.academiccalendar', 'Class',readonly = True),
        'start_date':fields.date('Start Date'),
        'status': fields.selection([('Active','Active'),('Closed','Closed'),('Cancelled','Cancelled')],'Status'),
        'exam_offered': fields.many2one('sms.exam.offered', 'Exam Offered',required=True ,readonly = True),
        'datesheet_lines' :fields.one2many('sms.exam.datesheet.lines', 'name', 'Datesheet Lines'),
        'result':fields.function(set_result, method=True,  string='Result(%)',type='float'),
        }
    
    _defaults = {
        'status': lambda *a: 'Active',
        }
    
    def get_month(self, cr, month):
        month_name = ""
        if month == 1:
            month_name = 'January'
        elif month == 2:
            month_name = 'February'
        elif month == 3:
            month_name = 'March'
        elif month == 4:
            month_name = 'April'
        elif month == 5:
            month_name = 'May'
        elif month == 6:
            month_name = 'June'
        elif month == 7:
            month_name = 'July'
        elif month == 8:
            month_name = 'August'
        elif month == 9:
            month_name = 'September'
        elif month == 10:
            month_name = 'October'
        elif month == 11:
            month_name = 'November'
        elif month == 12:
            month_name = 'December'
            
        return month_name

class sms_exam_datesheet_lines(osv.osv):
    """This objects stores papers and their dates, it is appeared as on2many to sms_exam_datesheet """
    
    def create(self, cr, uid, vals, context=None, check=True):
        super(osv.osv, self).create(cr, uid, vals, context)
        return None
    def unlink(self, cr, uid, ids, context={}, check=True):
        print "@@@@@exam datesheet lines@@@@",ids,context
        result = super(osv.osv, self).unlink(cr, uid, ids, context=context)
        return result
    
    def close_exam_subject(self, cr, uid, ds_id):
        """This method will do three things 
           it will de-activate entry when clicked the option on each subject in datesheet lines
           it will de-activate entry  on parent exams called when they are closed or canceled"""
        self.write(cr,uid,ds_id,{'open_for_edit':False})
        return result
    
    _name= "sms.exam.datesheet.lines"
    _descpription = "Stores exam date sheets paper and date"
    _columns = { 
        'name': fields.many2one('sms.exam.datesheet', 'Date Sheet',required=True),
        'subject': fields.many2one('sms.academiccalendar.subjects', 'Subject',required=True),
        'total_marks': fields.integer('Total Marks'),
        'paper_date': fields.date('Date'),
        'invigilator':fields.many2one('hr.employee', 'Invigilator'),
        'open_for_edit':fields.boolean('Open to Edit',readonly = 1)
    }
    
    _defaults = {
        'total_marks': lambda *a: 100
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        objs = self.browse(cr, uid, ids, context=context)
        for f in objs:
            std_sub_ids = self.pool.get('sms.student.subject').search(cr,uid,[('subject','=',f.subject.id)])
            exam_ids = self.pool.get('sms.exam.lines').search(cr,uid,[('name','=',f.name.id),('student_subject','in',std_sub_ids)])
            for exam in exam_ids:
                exam_obj = self.pool.get('sms.exam.lines').browse(cr, uid, exam, context=context)
                if exam_obj.obtained_marks > f.total_marks:
                    raise osv.except_osv(('Invalid Total Marks'),('Total marks should be greater than obtained marks. To change total marks, first change student obtained marks'))
            self.pool.get('sms.exam.lines').write(cr, uid, exam_ids, {'total_marks':f.total_marks})
        return {} 
       
sms_exam_datesheet_lines()    


#New Promotion

class sms_student_class_promotion(osv.osv):
    
    def set_promotion(self, cr, uid, ids, name, args, context=None):
       result = {}
       for obj in self.browse(cr, uid, ids, context=context):
           print "hello"
       return
    
    def show_students(self, cr, uid, ids, name, args, context=None):
       result = {}
       for obj in self.browse(cr, uid, ids, context=context):
           current_class = object.current_class.id
#            students = self.pool.get('sms.student').search(cr,uid,[('current_class',=obj.current_class.id))])
           if students:
               rec_students = self.pool.get('sms.student').browse(cr,uid,students)
               dict = {'name' :rec_students.id,
                       'std_existing_class_id':rec_students.current_class.id,
                       'father_name':rec_students.father_name,
                       'exam_to_show':datimetime.date.today(),
                       'obtained_marks':obj.id,
                       'total_marks':obj.id,
                       'parent_promotion_id':obj.id,
                       'decision':'',
                       }
        
       return
   
    def confirm_promotion(self, cr, uid, ids, name, args, context=None):
       result = {}
       for obj in self.browse(cr, uid, ids, context=context):
           print "hello"
       return
   
    def cancel_promotion(self, cr, uid, ids, name, args, context=None):
       result = {}
       for obj in self.browse(cr, uid, ids, context=context):
           print "hello"
       return
        
    def onchange_cunrrent_class(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        current_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, academiccalendar_id, context=context)
        sequence = current_obj.class_id.sequence
        class_id = self.pool.get('sms.classes').search(cr,uid,[('sequence','=',sequence+1)])
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr,uid,[('class_id','=',class_id),('state','in',['Draft','Active']),('session_id','!=',current_obj.session_id.id)])
        res = {'domain': {'promot_to_class': [('id', 'in', academiccalendar_ids)]}}
        return res
    
    _name= "sms.student.class.promotion"
    _descpription = "Stores exam date sheets"
    _columns = { 
        'name':fields.function(set_promotion, method=True,  size=256, string='Name',type='char'),
        'cunrrent_class': fields.many2one('sms.academiccalendar', 'Promote From',required=True),
        'promot_to_class': fields.many2one('sms.academiccalendar', 'Promote To',required=True),
        'dated': fields.date('Date',required=True),
        'promotion_by':fields.many2one('res.users', 'Promotion By',readonly=True),
        'promotion_line_ids':fields.one2many('sms.student.class.promotion.lines','parent_promotion_id','Parent ID'),
        'state': fields.selection([('Draft', 'Draft'),('Student_Loaded', 'Student Loaded'),('Promoted', 'Promoted'),('Cancelled', 'Cancelled')], 'State', readonly = True),
    }
    
    _defaults = {
                 'state':'Draft'
    }
    
sms_student_class_promotion()

class sms_student_class_promotion_lines(osv.osv):
    
    
    
    _name= "sms.student.class.promotion.lines"
    _descpription = "Stores exam date sheets"
    _columns = { 
        'name':fields.many2one('sms.student','Studet', readonly=True),
        'std_existing_class_id':fields.many2one('sms.academiccalendar','Academiccalendar From', readonly=True),
        'registration_no': fields.char('Registration No',size=256, readonly=True),
        'father_name': fields.char('Father Name',size=25, readonly=True),
        'exam_to_show': fields.many2one('sms.exam.datesheet','Exam', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
        'obtained_marks': fields.integer('Obtained Marks', readonly=True),
        'parent_promotion_id':fields.many2one('sms.student.class.promotion','Parent ID', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
        'decision': fields.selection([('Promote', 'Promote'),('Promote_Conditionally', 'Promote Conditionally'),('Suspended', 'Suspended'),('Failed', 'Failed'),('Pending', 'Pending')], 'Decision', required=True),
    }
    
    _defaults = {
    }

sms_student_class_promotion_lines()

#End new promotion




class sms_student_promotion(osv.osv):
    _name= "sms.student.promotion"
    _descpription = "Manage Student Promotion"
        
    def change_student_class_Journal_enteries(self, cr, uid, ids,current_class_id):
        ftlist = []
        print "student_id,", ids
        acad_cal = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.current_class_id)
        acd_cal_name = acad_cal.name
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        std = self.pool.get('sms.student').browse(cr,uid,ids)
        if user.company_id.enable_fm:
        
            fee_income_acc = user.company_id.student_fee_income_acc
            fee_expense_acc = user.company_id.student_fee_expense_acc
            fee_journal = user.company_id.fee_journal
            period_id = self.pool.get('account.move')._get_period(cr, uid, context)
#             if paymethod=='Cash':
#                 fee_reception_acc = user.company_id.fee_reception_account_cash
#                 if not fee_reception_acc:
#                     raise osv.except_osv(('Cash Account'), ('No Account is defined for Payment method:Cash'))
#             elif paymethod=='Bank':
#                 fee_reception_acc = user.company_id.fee_reception_account_bank
#                 if not fee_reception_acc:
#                     raise osv.except_osv(('Bank Account'), ('No Account is defined for Payment method:Bank'))
            fee_reception_acc = user.company_id.fee_reception_account_cash
            if not fee_income_acc:
                raise osv.except_osv(('Accounts'), ('Please define Fee Income Account'))
            if not fee_expense_acc:
                raise osv.except_osv(('Accounts'), ('Please define Fee Expense Account'))
            if not fee_journal:
                raise osv.except_osv(('Accounts'), ('Please Define A Fee Journal'))
            if not period_id:
                raise osv.except_osv(('Financial Period'), ('Financial Period is not defined in Fiscal Year.'))
        
        ################################################3
       
            
                # Delete fees of old class
            cls_fees_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',ids[0]),('acad_cal_id','=',current_class_id)])
            journals_updated = True

            for rec in cls_fees_ids:
                cls_fees_rec = self.pool.get('smsfee.studentfee').browse(cr,uid,rec)
                if cls_fees_rec.reconcile ==True and cls_fees_rec.paid_amount >0:
                    if user.company_id.enable_fm:
                        
                        
                        account_move_dict= {
                                        'ref':'Fee Adjusted(Student Deleted):',
                                        'journal_id':fee_journal.id,
                                        'type':'journal_voucher',
                                        'narration':str(std.name) +'--'+ str(acd_cal_name)}
                        
                        move_id=self.pool.get('account.move').create(cr, uid, account_move_dict, context)
                        account_move_line_dict=[
                            {
                                 'name': 'Student Deleted:--'+str(std.name),
                                 'debit':cls_fees_rec.paid_amount,
                                 'credit':0.00,
                                 'account_id':fee_income_acc.id,
                                 'move_id':move_id,
                                 'journal_id':fee_journal.id,
                                 'period_id':period_id
                             },
                            {
                                 'name': 'Student Deleted:--'+str(std.name),
                                 'debit':0.00,
                                 'credit':cls_fees_rec.paid_amount,
                                 'account_id':fee_reception_acc.id,
                                 'move_id':move_id,
                                 'journal_id':fee_journal.id,
                                 'period_id':period_id
                             }]
                        context.update({'journal_id': fee_journal.id, 'period_id': period_id})
                        for move in account_move_line_dict:
                            result=self.pool.get('account.move.line').create(cr, uid, move, context)
                            if not result:
                                journals_updated = False
            if journals_updated:
                return True
            else:
                return False
    
    def change_student_class_delete_student_data(self, cr, uid, ids,class_id,new_class_id):
        ftlist = []
        std = self.pool.get('sms.student').browse(cr,uid,obj.name.id)
        acad_cal = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.class_id)
        student_class_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',ids),('name','=',class_id),('state','=',"Current")])
        acd_cal_name = acad_cal.name
            
                
        std_subs = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',ids),('subject_status','=','Current')])
        for sub in std_subs:
            del_subs = self.pool.get('sms.student.subject').unlink(cr,uid,sub)
        # Delete fees of old class
        cls_fees_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',ids),('acad_cal_id','=',class_id)])
                
        for rec in cls_fees_ids:
                       
            #delete this from receiptbooklines
            del_fee1 = """DELETE FROM smsfee_receiptbook_lines WHERE student_fee_id ="""+str(rec)
            cr.execute(del_fee1)
            done_del = cr.commit()
            if done_del:
                #Delete this fee from student fee
                del_fee2 = self.pool.get('smsfee.studentfee').unlink(cr,uid,rec)
                 
                 #Delete Class History
                del_class = self.pool.get('sms.academiccalendar.student').unlink(cr,uid,obj.student_class_id[0])
                if del_class:
                    new_cls_id = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                        'name':new_class_id,                                                       
                        'std_id':ids,
                        'date_registered':datetime.date.today(), 
                        'state':'Current' })
                    if new_cls_id:
                        #add subjects to students
                        self.pool.get('sms.student').write(cr, uid, [ids], {'current_class':new_class_id})
                        acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',new_class_id),('state','!=','Closed')])
                        for sub in acad_subs:
                            add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                            'student': new_cls_id,
                            'student_id': ids,
                            'subject': sub,
                            'subject_status': 'Current'})
                        
                        #Now add newfees added from wziard
                        sql_ft = """SELECT id from smsfee_feetypes WHERE subtype IN('at_admission','Monthly_Fee','Annual_fee')"""
                        cr.execute(sql_ft)
                        ft_ids = cr.fetchall() 
                          
                        for ft in ft_ids:
                            ftlist.append(ft[0])
                        ftlist = tuple(ftlist)
                        ftlist = str(ftlist).rstrip(',)')
                        ftlist = ftlist+')'
        #               first insert all non motnly fees(search for fee with subtype at_admission) 
                        if ft_ids:
                            sqlfee1 =  """SELECT smsfee_classes_fees.id from smsfee_classes_fees
                                                INNER JOIN smsfee_feetypes
                                                ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                                WHERE smsfee_classes_fees.academic_cal_id ="""+str(obj.sms_academiccalendar_to.id)+"""
                                                AND smsfee_classes_fees.fee_structure_id="""+str(obj.fee_str.id)+"""
                                                AND smsfee_feetypes.subtype <>'Monthly_Fee'
                                                AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
                            cr.execute(sqlfee1)
                            fees_ids = cr.fetchall()  
                            if fees_ids: 
                                late_fee = 0
                                for idds in fees_ids:
                                    obj2 = self.pool.get('smsfee.classes.fees').browse(cr,uid,idds[0])
                                    crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                    'student_id': ids,
                                    'acad_cal_id': new_class_id,
                                    'acad_cal_std_id': new_cls_id,
                                    'date_fee_charged': datetime.date.today(),
                                    'fee_type': obj2.id,
                                    'due_month': obj.fee_starting_month.id,
                                    'fee_amount': obj2.amount,
                                    'paid_amount':0,
                                    'total':obj2.amount + late_fee,
                                     'state':'fee_unpaid',
                                    })
                            else:
                                  msg = 'Fee May be defined but not set for New Class:'        
        #                 # now insert all month fee , get it from the classes with a fee structure and then insert
                            sqlfee2 =  """SELECT smsfee_classes_fees.id from smsfee_classes_fees
                                        INNER JOIN smsfee_feetypes
                                        ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                                        WHERE smsfee_classes_fees.academic_cal_id ="""+str(obj.sms_academiccalendar_to.id)+"""
                                        AND smsfee_classes_fees.fee_structure_id="""+str(obj.fee_str.id)+"""
                                        AND smsfee_feetypes.subtype ='Monthly_Fee'
                                        AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
                    
                            cr.execute(sqlfee2)
                            fees_ids2 = cr.fetchall() 
                            #get update month of the class
                            updated_month = new_cal_obj.fee_update_till.id
                            #Now brows its session month ids, that will be saved as fee month 
                            session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',new_cal_obj.session_id.id),('id','>=',obj.fee_starting_month.id)]) 
                            rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)       
                            for month1 in rec_months:
                                if month1.id <= updated_month:
                                    late_fee = 0
                                    for fee in fees_ids2:
                                        obj3 = self.pool.get('smsfee.classes.fees').browse(cr,uid,fee[0])
                                        create_fee2 = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                        'student_id': obj.name.id,
                                        'acad_cal_id': obj.sms_academiccalendar_to.id,
                                        'date_fee_charged': datetime.date.today(),
                                        'acad_cal_std_id': new_cls_id,
                                        'fee_type': obj3.id,
                                        'fee_month': month1.id,
                                        'due_month': month1.id,
                                        'fee_amount': obj3.amount,
                                        'total': obj3.amount + late_fee,
                                         'state':'fee_unpaid',
                                        })
                                    
                        else:
                            raise osv.except_osv(('No Fee Found'),('Please Define a Fee For students promotion'))
        return 
    
    _columns = { 
        'student':fields.many2one('sms.student','StudentID', readonly=True),
        'sms_academiccalendar_student':fields.many2one('sms.academiccalendar.student','Student Academiccalendar', readonly=True),
        'sms_academiccalendar_student_to':fields.many2one('sms.academiccalendar.student','Student Academiccalendar', readonly=True),
        'sms_academiccalendar_from':fields.many2one('sms.academiccalendar','Academiccalendar From', readonly=True),
        'sms_academiccalendar_to':fields.many2one('sms.academiccalendar','Academiccalendar To', readonly=True),
        'registration_no': fields.char('Registration No',size=256, readonly=True),
        'name': fields.char('Student Name',size=25, readonly=True),
        'father_name': fields.char('Father Name',size=25, readonly=True),
        'obtained_marks': fields.integer('Obtained Marks', readonly=True),
        'total_marks': fields.integer('Total Marks', readonly=True),
        'decision': fields.selection([('Promote', 'Promote'),('Promote_Conditionally', 'Promote Conditionally'),('Suspended', 'Suspended'),('Failed', 'Failed'),('Pending', 'Pending')], 'Decision', required=True),
    }
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        print "write called"
        objs = self.browse(cr, uid, ids, context=context)
        for obj in objs:
            new_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.sms_academiccalendar_to.id)
            
            state = ""
            if obj.decision == 'Promote':
                self.pool.get('sms.academiccalendar.student').write(cr, uid, [obj.sms_academiccalendar_student.id], {'state':'Promoted',})
            elif obj.decision == 'Promote_Conditionally':
                self.pool.get('sms.academiccalendar.student').write(cr, uid, [obj.sms_academiccalendar_student.id], {'state':'Conditionally_Promoted',})
            elif obj.decision == 'Promote':
                self.pool.get('sms.academiccalendar.student').write(cr, uid, [obj.sms_academiccalendar_student.id], {'state':'Suspended',})
            elif obj.decision == 'Failed':
                self.pool.get('sms.academiccalendar.student').write(cr, uid, [obj.sms_academiccalendar_student.id], {'state':'Failed',})
                self.pool.get('sms.student').write(cr, uid, [obj.student.id], {'current_state':'Failed'})
   
                
            if obj.decision == 'Promote' or obj.decision == 'Promote_Conditionally':
                academiccalendar_student = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                    'name':obj.sms_academiccalendar_to.id,                                                       
                    'std_id':obj.student.id,
                    'date_registered':datetime.date.today(), 
                    'state':'Current' })
                if academiccalendar_student:
                    update_std = self.pool.get('sms.student').write(cr, uid, [obj.student.id], {'current_class':obj.sms_academiccalendar_to.id})
                    
                    acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',obj.sms_academiccalendar_to.id),('state','!=','Closed')])
                    for sub in acad_subs:
                        add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                        'student': academiccalendar_student,
                        'student_id': obj.student.id,
                        'subject': sub,
                        'subject_status': 'Current'})
                        
                    #Update student fees.
                    rec_std = self.pool.get('sms.student').browse(cr, uid, obj.student.id)
                    std_fs = rec_std.fee_type.id
                    updated_month = new_cal_obj.fee_update_till.id
                    #get all fees for the new class
                    sqlfee1 =  """SELECT smsfee_classes_fees.id,smsfee_feetypes.id,smsfee_feetypes.subtype
                            FROM smsfee_classes_fees
                            INNER JOIN smsfee_feetypes
                            ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                            WHERE smsfee_classes_fees.academic_cal_id ="""+str(new_cal_obj.id)+"""
                            AND smsfee_classes_fees.fee_structure_id="""+str(std_fs)+"""
                            AND smsfee_feetypes.subtype IN('Promotion_Fee','Monthly_Fee','Annual_fee')
                            """
                    cr.execute(sqlfee1)
                    fees_ids = cr.fetchall() 
                    if fees_ids:
                        late_fee = 0
                        fee_month = ''
                        for idds in fees_ids:
                        
                            obj2 = self.pool.get('smsfee.classes.fees').browse(cr,uid,idds[0])
                            if idds[2] == 'Monthly_Fee':
                                print "it is monthly fee"
                                session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',new_cal_obj.session_id.id)]) 
                                print "session months",session_months
                                print "fee updated till",updated_month
                                rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)
                                for month in rec_months:
                                    if month.id <= updated_month:
                                        print "calling method"
                                        insert_monthly_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                            'student_id': obj.student.id,
                                            'acad_cal_id': new_cal_obj.id,
                                            'acad_cal_std_id': academiccalendar_student,
                                            'fee_type': obj2.id,
                                            'generic_fee_type':idds[1],
                                            'date_fee_ch1arged':datetime.date.today(),
                                            'due_month': month.id,
                                            'fee_month':month.id,
                                            'fee_amount': obj2.amount,
                                            'paid_amount':0,
                                            'late_fee':0,
                                            'total_amount':obj2.amount + late_fee,
                                            'reconcile':False,
                                            'state':'fee_unpaid'
                                            })
                            else:
                                print "executing else"  
                                crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                            'student_id': obj.student.id,
                                            'acad_cal_id': new_cal_obj.id,
                                            'acad_cal_std_id': academiccalendar_student,
                                            'fee_type': obj2.id,
                                            'generic_fee_type':idds[1],
                                            'date_fee_ch1arged':datetime.date.today(),
                                            'due_month': updated_month,
                                            'fee_amount': obj2.amount,
                                            'paid_amount':0,
                                            'late_fee':0,
                                            'total_amount':obj2.amount + late_fee,
                                            'reconcile':False,
                                            'state':'fee_unpaid'
                                            })
                    else:
                          msg = 'Fee May be defined but not set for New Class:'
                ###################################################################
                std_class = self.pool.get('sms.academiccalendar.student').search(cr, uid,[('std_id', '=', obj.student.id),('state', '=', 'Current')])
                if not std_class:
                    continue
                acad_std = self.pool.get('sms.academiccalendar.student').browse(cr, uid,std_class[0])
#                 category2 = acad_std.name.class_id.category
                
#                 std_reg_type_exist = self.pool.get('sms.registration.nos').search(cr, uid,[('student_id', '=', obj.student.id),('class_category', '=', category2)])
#                 if not std_reg_type_exist:
#                     std_reg_nos = self.pool.get('sms.registration.nos').search(cr, uid,[('student_id', '=', obj.student.id)])
#                     self.pool.get('sms.registration.nos').write(cr, uid, std_reg_nos, {'is_active':False,})
#                     admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,std_class[0],acad_std.name.id)
#                     
#                     self.pool.get('sms.registration.nos').create(cr, uid, {
#                         'student_id': obj.student.id,
#                         'name': admn_no,
#                         'class_category': category2,
#                         'is_active': True,})
#                     self.pool.get('sms.student').write(cr, uid, obj.student.id, {'registration_no':admn_no,})
                ###################################################################3
    
                        
        return {} 
       
    _defaults = {
        'decision' : 'Pending',
    }

#########################################################

class sms_student_change_section(osv.osv):
    _name= "sms.student.change.section"
    _descpription = "Manage Student Change Section"

    _columns = { 
        'student':fields.many2one('sms.student','StudentID', readonly=True),
        'sms_academiccalendar_student':fields.many2one('sms.academiccalendar.student','Student Academiccalendar', readonly=True),
        'sms_academiccalendar_student_to':fields.many2one('sms.academiccalendar.student','Student Academiccalendar', readonly=True),
        'sms_academiccalendar_student_from':fields.many2one('sms.academiccalendar','Academiccalendar From', readonly=True),
        'sms_academiccalendar_to':fields.many2one('sms.academiccalendar','Academiccalendar To', readonly=True),
        'registration_no': fields.char('Registration No',size=256, readonly=True),
        'name': fields.char('Student Name',size=25, readonly=True),
        'father_name': fields.char('Father Name',size=25, readonly=True),
        'change_section':fields.boolean('Change Section'),
    }
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        objs = self.browse(cr, uid, ids, context=context)
        for obj in objs:
            new_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.sms_academiccalendar_to.id)
            
            if obj.change_section:
                self.pool.get('sms.academiccalendar.student').write(cr, uid, [obj.sms_academiccalendar_student.id], {'state':'section_changed','date_section_changed':datetime.date.today(),'section_changed_by':uid})
                std_subs = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',obj.sms_academiccalendar_student.id),('subject_status','=','Current')])
                for sub in std_subs:
                    add_subs = self.pool.get('sms.student.subject').write(cr,uid,sub,{'subject_status': 'Suspended'})
                #udpate academic calendar old object strength redude by 1 
#                 print "old acad cal::",obj.sms_academiccalendar_student_from.id
#                 print "new acad_cal::",obj.sms_academiccalendar_to.id
#                 cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.sms_academiccalendar_student_from)
#                 cur_strength = cal_obj.cur_strength
#                 cur_strength = int(cur_strength) - 1
#                 update_acad_cal = self.pool.get('sms.academiccalendar').write(cr, uid, obj.sms_academiccalendar_student_from.id, {'cur_strength':cur_strength})
      
            if obj.change_section:
                acad_student = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',obj.sms_academiccalendar_to.id),('std_id','=',obj.student.id)])
                if acad_student:
                    academiccalendar_student = acad_student[0]
                    self.pool.get('sms.academiccalendar.student').write(cr,uid,academiccalendar_student,{'date_registered':datetime.date.today(), 'state':'Current' })
                    if academiccalendar_student:
                        update_std = self.pool.get('sms.student').write(cr, uid, [obj.student.id], {'current_class':obj.sms_academiccalendar_to.id})

                        student_subject_ids = self.pool.get('sms.student.subject').search(cr,uid,[('student_id','=',obj.student.id),('student','=',academiccalendar_student)])
                        for student_subject_id in student_subject_ids:
                            self.pool.get('sms.student.subject').write(cr,uid,student_subject_id,{'subject_status': 'Current'})     
                else:
                    academiccalendar_student = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                        'name':obj.sms_academiccalendar_to.id,                                                       
                        'std_id':obj.student.id,
                        'date_registered':datetime.date.today(), 
                        'state':'Current' })
                    if academiccalendar_student:
                        update_std = self.pool.get('sms.student').write(cr, uid, [obj.student.id], {'current_class':obj.sms_academiccalendar_to.id})
    #                     #udpate academic calendar new object strength increment by 1
    #                     cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,obj.sms_academiccalendar_to.id)
    #                     cur_strength = cal_obj.cur_strength
    #                     print 
    #                     cur_strength = int(cur_strength) + 1
    #                     update_acad_cal = self.pool.get('sms.academiccalendar').write(cr, uid, obj.sms_academiccalendar_student_from.id, {'cur_strength':cur_strength})
                        
                        #uadd subjects to students
                        acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',obj.sms_academiccalendar_to.id),('state','!=','Closed')])
                        for sub in acad_subs:
                            add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                            'student': academiccalendar_student,
                            'student_id': obj.student.id,
                            'subject': sub,
                            'subject_status': 'Current'})                        
        return {} 
       
    _defaults = {
        'change_section': lambda *a: False,
    }

class sms_change_student_class(osv.osv):

    
    def onchange_student(self, cr, uid,ids,std):
        result = {}
        if std:
             std_rec = self.pool.get('sms.student').browse(cr, uid, std)
#              result['fee_str'] = std_rec.fee_type.id
             result['father_name'] = std_rec.father_name
             result['current_class'] = std_rec.current_class.id
# #              update_lines = self.pool.get('smsfee.receiptbook').write(cr, uid, ids, {'father_name':father_name})
             print "result:::",result
        return {'value':result}
    
    def chang_student_class(self, cr, uid,ids,std):
        result = {}
        if std:
             std_rec = self.pool.get('sms.student').browse(cr, uid, std)
#              result['fee_str'] = std_rec.fee_type.id
             result['father_name'] = std_rec.father_name
             result['current_class'] = std_rec.current_class.id
# #              update_lines = self.pool.get('smsfee.receiptbook').write(cr, uid, ids, {'father_name':father_name})
             print "result:::",result
        return {'value':result}
    def _set_default_uid(self, cr, uid, context={}):
        return uid
    
    def onchange_acad_cal(self, cr, uid, ids, acad_cal):
        result = {}
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal)
        acad_session_id = acad_cal_obj.acad_session_id.id
       
        #result['academic_session'] = acad_session_id 
        #result['fee_update_till'] = acad_cal_obj.fee_update_till.id
        session_id = self.pool.get('sms.session').search(cr, uid, [('academic_session_id','=', acad_session_id),('state','=', 'Active')])
        if session_id:
            print "session found:",session_id
            result['session'] = session_id[0]
        return {'value': result}
    
    
    _name= "sms.change.student.class"
    _descpription = "Manage Student Change Class"

    _columns = { 
        'name':fields.many2one('sms.student','Student',domain="[('state','=','Admitted')]", required=True),
        'father_name': fields.char('Father Name',size=25,),
        'current_class':fields.many2one('sms.academiccalendar','Current Class', readonly=True),
        'session': fields.many2one('sms.session', 'Session', domain="[('state','!=','Previous'),('academic_session_id','=',academic_session)]", help="Student will be admitted belongs to selected session",readonly = True),
        'new_class':fields.many2one('sms.academiccalendar','New Class', domain="[('state','!=','Complete'),('id','!=',current_class)]", required=True),
        'changed_by':fields.many2one('res.users','Changed By'),
        'date_changed':fields.date('Date'),
        'reason':fields.text('Reason'),
        'state': fields.selection([('Draft', 'Draft'),('Confirm','Confirm'),('Class_changed', 'Class Changed')], 'State', readonly=True),
    }
    _defaults = {
                 'state':'Draft',
                 'date_changed': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
                 'changed_by': _set_default_uid,
        }
    def on_change(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'Confirm'})
        return True
    
    def on_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'Draft'})
        return {'type': 'ir.actions.act_window_close'}

        
    def on_confirm(self, cr, uid, ids,context):
        cur_obj= self.browse( cr,uid,ids )
        for obj in cur_obj:
            current_std_id=obj.name.id 
            new_cls_id=obj.new_class.id
        #suspend student in sms.academiccalendar.student
        print "student name is",obj.name.name, "student id is",current_std_id
        print "new class is",obj.new_class.name,"class id is",new_cls_id
        current_stu=self.pool.get('sms.academiccalendar.student').search(cr, uid, [('std_id','=',current_std_id)])
        print current_stu
        if current_stu:
            for stu_id in current_stu:
                 self.pool.get('sms.academiccalendar.student').write(cr, uid, stu_id, {'state': 'Suspended'})
            #suspend subjects of this student
        current_sub=self.pool.get('sms.student.subject').search(cr, uid, [('student_id','=',current_std_id)])
        for sub_id in current_sub:
             self.pool.get('sms.student.subject').write(cr, uid, sub_id, {'subject_status': 'Suspended'})
#       assign new class id to this student
        new_cl_id = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                    'name':new_cls_id,                                                     
                    'std_id':current_std_id,
                    'date_registered':datetime.date.today(), 
                    'state':'Current' })
        #assign new class subjects
        new_cls_sub=self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=',new_cls_id)])
        if new_cls_sub:
            for subject in new_cls_sub:
                self.pool.get('sms.student.subject').create(cr ,uid ,{
                                                                    'student' : new_cl_id,
                                                                    'student_id' :obj.name.id,
                                                                    'subject' : subject,
                                                                    'subject_status' : 'Current' ,
                                                                    })
        

        self.write(cr, uid, ids, {'state': 'Class_changed'})
        return True
        
sms_change_student_class()
       
   
class hr_employee(osv.osv):
    """This object is used to add fields in employee"""
    _name = 'hr.employee'
    _inherit ='hr.employee'
        
    _columns = {
        'father_name': fields.char("Father Name", size=32),
    }
hr_employee()

class sms_registration_format(osv.osv):
    """This object is used for regitration format"""
    _name = 'sms.registration.format'
    _descpription = "Manage SMS Registration Format"
    
    def set_format(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if ((obj.first == obj.second or obj.first == obj.third or obj.first == obj.fourth) and obj.first) or ((obj.second == obj.third or 
                obj.second == obj.fourth) and obj.second) or (obj.third == obj.fourth and obj.third): 
                raise osv.except_osv(('Invalid Format'), ('Repeatition in format, Please remove repetitions'))
            
            if obj.first != 'Counter' and obj.second != 'Counter' and obj.third != 'Counter' and obj.fourth != 'Counter':
                raise osv.except_osv(('Invalid Format'), ('Counter is missing'))
            
            format = ""
            if obj.first:
               format = format + str(obj.first)
            if obj.second:
               format = format + str(obj.separator_1) + str(obj.second) 
            if obj.third:
               format = format + str(obj.separator_2) + str(obj.third) 
            if obj.fourth:
               format = format + str(obj.separator_3) + str(obj.fourth) 

            result[obj.id] = format
        return result

    _columns = {
        'name':fields.function(set_format, method=True,  size=256, string='Format',type='char'),
        'state':fields.boolean('Active'),
        'first': fields.selection([('Category', 'Category'),('Year', 'Year'),('Month', 'Month'),('Counter', 'Counter')], 'First', required=True),
        'separator_1': fields.selection([('-', '-'),('/', '/')], 'Seperator'),
        'second': fields.selection([('Category', 'Category'),('Year', 'Year'),('Month', 'Month'),('Counter', 'Counter')], 'Second'),
        'separator_2': fields.selection([('-', '-'),('/', '/')], 'Seperator'),
        'third': fields.selection([('Category', 'Category'),('Year', 'Year'),('Month', 'Month'),('Counter', 'Counter')], 'Third'),
        'separator_3': fields.selection([('-', '-'),('/', '/')], 'Seperator'),
        'fourth': fields.selection([('Category', 'Category'),('Year', 'Year'),('Month', 'Month'),('Counter', 'Counter')], 'Fourth'),
        'counter_reset':fields.boolean('Reset Counter with Session'),
    }
sms_registration_format()
#################################

class sms_student_clearance(osv.osv):
    """This object defines students' certificates issuance process."""
    
#     def onchange_class(self, cr, uid,ids,class_id):
#         result = {}
#         if class_id:
#              class_rec = self.pool.get('sms.academiccalendar').browse(cr, uid, class_id)
#              father_name = std_rec.father_name
#              result['father_name'] = father_name
#              result['requested_by'] = uid
#              self.pool.get('sms.student.clearance').write(cr, uid, ids, {'father_name':father_name,'requested_by':uid}) #this line is to update or save father name in sms.student.clearance table 
#         
#         return {'value':result}
#     
    def onchange_student(self, cr, uid,ids,student_id):
        result = {}
        if student_id:
             std_rec = self.pool.get('sms.student').browse(cr, uid, student_id)
             father_name = std_rec.father_name
             result['father_name'] = father_name
             #result['requested_by'] = uid
             #self.pool.get('sms.student.clearance').write(cr, uid, ids, result) #this line is not required here as we dont store/save runtime data in tables 
             
        return {'value':result}
    
    def on_button_approved(self, cr, uid, ids, context=None):
         result = {}
         result['date_approved'] = datetime.date.today()
         result['approved_by'] = uid
         result['state'] = 'Approved'
         self.pool.get('sms.student.clearance').write(cr, uid, ids, result)#this line will update table and save the record in sms.student.clearance table
       
    def on_button_issued(self, cr, uid, ids, context=None):
        result = {}
        obj = self.browse(cr, uid, ids[0])
        result['date_issued'] = datetime.date.today()
        result['issued_by'] = uid
        result['state'] = 'Issued'
         #for every record in certificate object we will repeat some changes, so we will do it through for loop
        for certificate in obj.certificate:
            #in the counter field of sms_student_certificate select maximum value(i.e most updated) for current selected certificate, and add 1 to it.. certificate.id is integer value so converted it to string by str as where only work on string value
            sql = """SELECT MAX(counter) + 1 FROM sms_student_certificate
                WHERE certificate = """ + str(certificate.id)            
            #execute these changes
            cr.execute(sql)
            row = cr.fetchone()
#            print obj.name.id #just to check that obj.name.id is fetching vlaue or not
#            print certificate.id #just to check that certificate.id is fetching vlaue or not

            #To check whether a student has already been issued a certificate?, check any id exist in sms.student.certificate object for selected student and selected certificate
            id_exist = self.pool.get('sms.student.certificate').search(cr, uid, [('name','=', obj.name.id),('certificate','=', certificate.id)])
            #if any id exists for selected student and selected certificate, it means this student has been already awarded with certificate, and he is applyin for duplicate 
            if id_exist:
                #Select that whole record on the basis of existed current id_exis[0]
                obj_exist = self.pool.get('sms.student.certificate').browse(cr, uid, id_exist[0], context)
                #now using above fetched object obj_exist update the student_issuance field by incrementing it 1, that this student was issued this certificate 1 more time (i.e duplicate)
                self.pool.get('sms.student.certificate').write(cr, uid, id_exist, {'student_issuance': obj_exist.student_issuance + 1})
            #otherwise if the id_exist does not exist in the sms.student.certificate table, so the student is applying first time for certificate               
            else:
                #thus select the sms.student.certificate table and insert the following values for the selected fields
                self.pool.get('sms.student.certificate').create(cr,uid,{
                    'name':obj.name.id,
                    'certificate':certificate.id,
                    'certificate_number':str(obj.name.registration_no) + "-" + str(row[0]), # this is format for certificate number which will combine student registration number and counter value
                    #set the current value of counter equal to zero, and as the first student is issued certificate coounter will start incrementing by 1.                                                   
                    'counter':row[0],                                                    
                    'student_issuance':1,                                                    
                    })

        self.pool.get('sms.student.clearance').write(cr, uid, ids, result)#this line will update table and save the record in sms.student.clearance table
    
    def _set_default_uid(self, cr, uid, context={}):
        return uid
    
    _name = 'sms.student.clearance'
    _description = "defines certificate issuance process"
    _columns = {
        'student_class':fields.many2one('sms.academiccalendar','Class', required = True,),        
        'name': fields.many2one('sms.student','Student Name', domain="[('current_class','=',student_class),('state','in',['Admitted','admission_cancel','drop_out','slc'])]", required=True),
        'certificate': fields.many2many('sms.certificate', 'sms_clearance_certificate_rel', 'clearance', 'certificate', 'Certificates', required=True),
        'father_name': fields.char(string = 'Father',size = 100),
        #'certificate_type': fields.selection([('School Leaving Certificate', 'School Leaving Certificate'),('Sports Certificate', 'Sports Certificate'),('Course Completion Certificate', 'Course Completion Certificate'),('Character Certificate', 'Character Certificate')], 'Certificate Type', required=True),
        'paid_amount':fields.integer('Paid Amount'),
        'date_requested':fields.date('Date Requested', readonly=True),
        'requested_by':fields.many2one('res.users','Requested By', readonly=True),
        'date_approved':fields.date('Date Approved', readonly=True),
        'approved_by':fields.many2one('res.users','Approved By', readonly=True),
        'date_issued':fields.date('Date Issued', readonly=True),
        'issued_by':fields.many2one('res.users','Issued By', readonly=True),
        'state': fields.selection([('Draft', 'Draft'),('Approved', 'Approved'),('Rejected', 'Rejected'),('Issued', 'Issued')], 'State', required=True, readonly=True),
        'certificate_number':fields.char('Certificate No', readonly=True),
        
    } 
    _defaults = {'state': 'Draft',
                 'date_requested': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
                 'requested_by': _set_default_uid,}
    #_sql_constraints = [('certificate_number_unique', 'unique (certificate_number)', """Certificate Number must be unique. """)]         

sms_student_clearance()    
    
class student_admission_register(osv.osv):

    def _get_student(self, cr, uid, context={}):
        if context:
            return context['name']
        return None

    def student_father(self, cr, uid, context={}):
        if context:
            return context['father_name']
        return None
    
    def unlink(self, cr, uid, ids, context={}, check=True):
        result = super(osv.osv, self).unlink(cr, uid, ids, context=context)
        return None    
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return True
    
    def load_subjects(self, cr, uid, ids, context):
        student_class = ""
        for stu_ids in self.browse( cr,uid,ids ):
            student_class = stu_ids.student_class.id
            class_id = self.pool.get('sms.academiccalendar').search(cr ,uid ,[('id','=',student_class),('group_id','=',stu_ids.group.id)])
            if stu_ids.group.name == 'No group':
                class_id = self.pool.get('sms.academiccalendar').search(cr ,uid ,[('id','=',student_class)])
                
        ac_sub_obj_ids =  self.pool.get('sms.academiccalendar.subjects').search(cr ,uid ,[('academic_calendar','=',class_id),('state','!=','Complete')])
        for acd_subj_id in self.pool.get('sms.academiccalendar.subjects').browse(cr ,uid ,ac_sub_obj_ids):
            self.pool.get('admission.register.subjects').create(cr ,uid ,{'name': acd_subj_id.id ,
                                                                                                 'parent_id': ids[0],
                                                                                                  } )
        return True
    
    def cancel_admisssion_registration(self, cr, uid, ids, context):
        subj_ids = self.pool.get('admission.register.subjects').search(cr ,uid ,[('parent_id','=',ids[0])])
        self.pool.get('admission.register.subjects').unlink(cr ,uid ,subj_ids)
        fee_ids = self.pool.get('admission.register.fees').search(cr ,uid ,[('name','=',ids[0])])
        self.pool.get('admission.register.fees').unlink(cr ,uid ,fee_ids)
        self.write(cr, uid, ids, {'state': 'Draft'})
        return True
    
    def confirm_student_subjects(self, cr, uid, ids, context):
        for info in self.browse(cr ,uid ,ids):
            ac_stu_id= self.pool.get('sms.academiccalendar.student').create(cr ,uid ,{
                                                                'name': info.student_class.id ,
                                                                'std_id':info.name.id ,             
                                                                'state':'Current' ,             
                                                                'date_registered':datetime.date.today() ,             
                                                                 })
            for subs in info.subject_ids:
                stu_sub_obj_id = self.pool.get('sms.student.subject').create(cr ,uid ,{
                                                                'student' : ac_stu_id,
                                                                'student_id' : info.name.id,
                                                                'subject' : subs.name.id,
                                                                'subject_status' : 'Current' ,
                                                                })
            admission_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr ,uid ,ac_stu_id ,info.student_class.id)
            self.pool.get('sms.student').write(cr, uid, info.name.id , {'registration_no':admission_no,'fee_starting_month':info.fee_starting_month.id,'fee_type':info.fee_structure.id, 'state': 'Admitted', 'current_state': 'Current','admitted_to_class':info.student_class.id,'admitted_on':datetime.date.today(),'current_class':info.student_class.id})
        return None
    
    def onchange_set_domain(self,cr ,uid ,ids ,student_class ,context=None):
        acad_cal_id_group = []
        group = ''
        for adcal_id in self.pool.get('sms.academiccalendar').browse(cr ,uid ,[student_class]):
            acad_cal_id_group.append(adcal_id.group_id.id)
        group = adcal_id.group_id.id
        
        return {'domain': {'fee_starting_month': [('session_id','=',adcal_id.session_id.id)] ,
                            'group':[('id','in',acad_cal_id_group ) ]},
                    'value':{'group':group}}

    def onchange_form_no(self,cr ,uid ,ids ,name ,context=None):
        val = {}
        rec = self.pool.get('sms.student').browse(cr ,uid ,name)
            
        val['gender'] = rec.gender
        val['birthday'] = rec.birthday
        val['blood_grp'] = rec.blood_grp
        val['father_occupation'] = rec.father_occupation
        val['father_nic'] = rec.father_nic
        val['religion'] = rec.religion
        val['phone'] = rec.phone
        val['cell_no'] = rec.cell_no
        val['fax_no'] = rec.fax_no
        val['email'] = rec.email
        val['cur_address'] = rec.cur_address
        val['cur_city'] = rec.cur_city
        val['cur_country'] = rec.cur_country.id
        val['permanent_address'] = rec.permanent_address
        val['permanent_country'] = rec.permanent_country
        val['permanent_country'] = rec.permanent_country.id
        val['domocile'] = rec.domocile
        
        #-----------------calculate form value----------------------------
        sql = """ select count (*) from student_admission_register"""
        cr.execute(sql)
        form_no = cr.fetchone()[0]
        val['form_no'] = form_no
        return {'value': val}

    
    """This object is store admission details regarding to student register """
    _name="student.admission.register"
    _columns = {
        'name' : fields.many2one('sms.student' , 'Student Name'),
        'father_name' : fields.char('Father Name', readonly=True ,size=256),
        'fee_structure' : fields.many2one('sms.feestructure' , 'Fee structure'),
        'fee_start_from' : fields.date('Fee Start From'),
        'fee_starting_month': fields.many2one('sms.session.months', 'Starting Fee Month'),
        'student_class' : fields.many2one('sms.academiccalendar' , 'Student Class',domain="[('admission_closed','=',False),('state','=','Close')]"),
        'group' : fields.many2one('sms.group' ,'Group'),
        'subject_ids' : fields.one2many('admission.register.subjects','parent_id','Student Subjects'),
        'form_no' : fields.integer('Form No'),
        'total_fee' : fields.integer('Total Fee'), 
        'state': fields.selection([('Draft', 'Draft'),('waiting_approval', 'Waiting Approval'),('Confirm', 'Confirm')], 'State', readonly = True),
        #*********************personal info************************************88
        'gender': fields.selection([('Male', 'Male'),('Female', 'Female')], 'Gender'),
        'birthday': fields.date("Date of Birth"),
        'blood_grp': fields.selection([('A+', 'A+'),('A-', 'A-'),('B+', 'B+'),('B-', 'B-'),('AB+', 'AB+'),('AB-', 'AB-'),('O+', 'O+'),('O-', 'O-')], 'Blood Group'),
        'father_occupation': fields.char(string = "Father Occupation", size=32),
        'father_nic': fields.char(string = "Father NIC", size=32),
        'religion': fields.char(string = "Religion", size=32),
        'phone': fields.char(string = "Phone No", size=32),
        'cell_no': fields.char(string = "Cell No", size=32),
        'fax_no': fields.char(string = "Fax No", size=32),
        'email': fields.char(string = "Email", size=32),
        'cur_address': fields.char(string = "Street", size=32),
        'cur_city': fields.char(string = "City", size=32), 
        'cur_country': fields.many2one('res.country', 'Country'),
        'permanent_address': fields.char(string = "Street", size=32),
        'permanent_city': fields.char(string = "City", size=32), 
        'permanent_country': fields.many2one('res.country', 'Country'), 
        'domocile': fields.char(string = "Domicile", size=32),
        
        
    } 
    _defaults = {  'state': lambda*a :'Draft' ,
                 'name':_get_student,
                 'father_name':student_father}
        
student_admission_register()
  
class admission_register_subjects(osv.osv):
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    _name = 'admission.register.subjects'
    _columns = {
        'name' : fields.many2one('sms.academiccalendar.subjects','Subjects'),
        'parent_id' : fields.many2one('student.admission.register','Student SUbject'),
    }
    _defaults = {    }    
admission_register_subjects()
 
# class sms_class_attendance(osv.osv):
#  
#     def mark_attendance(self, cr, uid, ids, context):
#          
#         rec = self.browse(cr ,uid ,ids)[0]
#         for acd_cal in rec.class_id.acad_cal_students:
#             create_line = self.pool.get('sms.class.attendance.lines').create(cr ,uid ,{
#                                                                     'parent_id': rec.id ,
#                                                                     'student_name':acd_cal.std_id.id  ,
#                                                                     'student_class_id':acd_cal.id  ,
#                                                                     })
#         self.write(cr ,uid ,ids ,{'state':'waiting_approval' ,'class_teacher':rec.class_id.class_teacher.id })
#         return None
#          
#     def submit_attendance(self ,cr ,uid ,ids ,context):
#         print "submit_attendance"
#         attendance_state = ""
#         rec = self.browse(cr ,uid ,ids)[0]
#           
#         for a_lines in rec.child_id:
#             print a_lines.present,a_lines.absent,a_lines.leave
#             if a_lines.present == False and a_lines.absent == False and a_lines.leave == False:
#                 print "and"
#                 self.pool.get('sms.class.attendance.lines').write(cr ,uid ,a_lines.id ,{'state':'present' ,'present':True })
#             elif a_lines.present == True and a_lines.absent == False and a_lines.leave == False:
#                 self.pool.get('sms.class.attendance.lines').write(cr ,uid ,a_lines.id ,{'state':'present'})
#                  
#         #raise osv.except_osv(('Not Allowed'), ('S..................s.'))
#         self.write(cr ,uid ,ids ,{'state':'submit' , 'punched_by':uid})
#         return None
#      
#     def onchange_set_domain(self,cr ,uid ,ids ,class_id ,attendance_date ,context=None):
#         result = {}
#         rec = self.pool.get('sms.academiccalendar').browse(cr ,uid ,[class_id])[0]
#         print rec.class_teacher.name
#         current_day = datetime.datetime.now().strftime("%A")
#         if current_day != 'Sunday': 
#              
#             if attendance_date < rec.session_id.start_date or attendance_date > rec.session_id.end_date:
#                 raise osv.except_osv(('Invalid Date'), ('Your date should be within session i.e from   '+str(rec.session_id.start_date)+' to '+str(rec.session_id.end_date) ))
#             result['class_teacher'] = rec.class_teacher.id
#         else:
#             raise osv.except_osv(('Denied !'), ('Cannot punch date on Sunday.' ))
#          
#  
#         return {'value': result}
#      
#     """This object serves as a tree view for sms_student_admission_register for fee purpose """
#     _name = 'sms.class.attendance'
#     _columns = {
#         'name' : fields.char('Name',size=256),
#         'class_id' : fields.many2one('sms.academiccalendar',' Class' ,required=True),
#         'class_teacher' : fields.many2one('res.users',' Teacher Name' ),
#         'attendance_date' :fields.date('Date' ,required=True),
#         'punched_by' : fields.many2one('res.users','  Punched By'),
#         'child_id' : fields.one2many('sms.class.attendance.lines','parent_id','Student Attendance'),
#         'state' : fields.selection([('Draft','Draft'),('waiting_approval','waiting_approval'),('submit','submit')],'Status'),
#     }
#     _defaults = {'state': 'Draft'}  
#     _sql_constraints = [('class_date', 'unique(attendance_date,class_id)', 'Attendance for the selected class has already been punched.')]
#  
# sms_class_attendance()
#  
# class sms_class_attendance_lines(osv.osv):
#  
#     def onchange_set_absent(self,cr ,uid ,ids ,absent ,context=None):
#         result = {}
#         print "absen----",absent
#         if absent == True :
#             result['present'] = False 
#             result['leave'] = False
#             self.write(cr ,uid ,ids ,{'state':'absent' ,'absent':False ,'leave':False })
#          
#         return {'value': result}
#      
#     def onchange_set_leave(self,cr ,uid ,ids ,leave ,context=None):
#         result = {}
#         print "leave----",leave
#         if leave == True :
#             result['absent'] = False 
#             result['present'] = False
#             self.write(cr ,uid ,ids ,{'state':'leave' ,'absent':False ,'leave':False })
#          
#         return {'value': result}
#      
#     def onchange_set_present(self,cr ,uid ,ids ,present ,context=None):
#         result = {}
#         print "present----",present
#         if present == True :
#             result['absent'] = False 
#             result['leave'] = False
#             self.write(cr ,uid ,ids ,{'state':'present' ,'absent':False ,'leave':False })
#          
#         return {'value': result}
#          
# #     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):                
# #         raise osv.except_osv(('Not Allowed'), ('S..................s.'))
# #         return
#      
#     """This object serves as a tree view for sms_student_admission_register for fee purpose """
#     _name = 'sms.class.attendance.lines'
#     _columns = {
#         'parent_id' : fields.many2one('sms.class.attendance','Class Attendance'),
#      #   'student_name' : fields.char('Student',size=256),
#         'student_name' : fields.many2one('sms.student','Student'),
#         'student_class_id' : fields.many2one('sms.academiccalendar.student','Student Class'),
#         'present' :fields.boolean('present'),
#         'absent' :fields.boolean('absent'),
#         'leave' :fields.boolean('leave'),
#         'state' : fields.selection([('Draft','Draft'),('present','Present'),('absent','Absent'),('leave','Leave')],'Status'),
#     }
#     _defaults = {'state': 'Draft' , 'present': True }    
#      
# sms_class_attendance_lines()

