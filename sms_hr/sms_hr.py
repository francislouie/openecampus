import time
import datetime
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dbus.decorators import method
import calendar
#from samba.netcmd import domain

DAYOFWEEK_SELECTION = [('0', 'Monday'),
                       ('1', 'Tuesday'),
                       ('2', 'Wednesday'),
                       ('3', 'Thursday'),
                       ('4', 'Friday'),
                       ('5', 'Saturday'),
                       ('6', 'Sunday'),

                       ]

class res_company(osv.osv):
    
    """This object inherits res company adds fields related to accounts ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
                'empleado_branch_id':fields.char('Branch ID')}

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    _description = 'Contract'
    
    def deduct_amount(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            
            mss = self.pool.get('hr.monthly.attendance.calculation').search(cr, uid, [('contract_id','=', f.id),('calendar_month','=', '2018-02-01')])
            if mss:
                rec = self.pool.get('hr.monthly.attendance.calculation').browse(cr,uid,mss[0]) 
                deducted_amount = rec.deducted_amount
                result[f.id] = deducted_amount 
            else:
                result[f.id] = 0.0
        return result
    _columns = {
        'attendance_calc': fields.one2many('hr.monthly.attendance.calculation','contract_id', "Attendance Calc"),
        'month': fields.char('Month (e.g 02-2018)'),
        'amount_to_deduct':fields.function(deduct_amount, method=True, string='Deducted Amount',type='float'),
    }


class hr_monthly_attendance_calculation(osv.osv):
    _name = "hr.monthly.attendance.calculation"
    _description = "Salary Calculation"
    
    def get_twentry_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            records = 0
            t20_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>','2018-02-01'),('attendance_date','<','2018-02-28')])
            if t20_ids:
                rect20 = self.pool.get('hr.employee.attendance').browse(cr,uid,t20_ids)
                for t20 in rect20:
                    late_m = t20.total_short_minutes
                    if late_m >=20 and late_m <30:
                        records = records +1
        result[f.id] = records
        return result
    
    def get_decuction_twentry_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_late = f.twenty_minutes_late or 0
            if total_late >=3:
                day_ded = int(total_late/3)
            else:
                day_ded = 0
            
            result[f.id] = day_ded
        return result
    
    
    def get_thirty_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            records = 0
            t20_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>','2018-02-01'),('attendance_date','<','2018-02-28')])
            if t20_ids:
                rect20 = self.pool.get('hr.employee.attendance').browse(cr,uid,t20_ids)
                for t20 in rect20:
                    late_m = t20.total_short_minutes
                    if late_m >=30:
                        records = records +1
            result[f.id] = records
        return result
    
    def get_decuction_thirty_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_late = f.thirty_minutes_late or 0
            if total_late >=2:
                day_ded = int(total_late/2)
            else:
                day_ded = 0
            
            result[f.id] = day_ded
        return result
    
    def get_absentess_leave(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            net= f.absentees_this_month - f.approved_leaves_this_month 
            if net <0:
                net = 0
            result[f.id] = net
        return result
    
    def absentess_plus_late_days(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            net= f.deduction_on_twenty_minutes_late or 0 + f.deduction_on_thirty_minutes_late or 0 + f.net_absentees 
            if net <0:
                net = 0
            result[f.id] = net
        return result
    
    def deducted_amoun(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            final_deducted_days= f.deducted_absentees_plus_late_comings
            salary = f.contract_id.wage or 0
            per_day = salary/30
            total_deductions = per_day * final_deducted_days 
            result[f.id] = total_deductions
        return result
    
    _columns = {
        'calendar_month': fields.date('Month', required=True),
        'name': fields.char('Month Year'),
        'contract_id': fields.many2one('hr.contract'),
        'employee_id': fields.many2one('hr.employee'),
        'twenty_minutes_late': fields.function(get_twentry_m_late, method=True, string='Twenty Minutes late',type='integer'),
        'deduction_on_twenty_minutes_late': fields.function(get_decuction_twentry_m_late, method=True, string='Deduction (Days) On 20min',type='integer'),
        'thirty_minutes_late': fields.function(get_thirty_m_late, method=True, string='Thirty Minutes late',type='integer'),
        'deduction_on_thirty_minutes_late': fields.function(get_decuction_thirty_m_late, method=True, string='Deduction (Days) On 30min',type='integer'),
        'absentees_this_month': fields.integer('Absentees This month'),
        'approved_leaves_this_month': fields.integer('Leaves This month'),
        'net_absentees': fields.function(get_absentess_leave, method=True, string='Absentees After Leave',type='integer'),
        'deducted_absentees_plus_late_comings': fields.function(absentess_plus_late_days, method=True, string='Absent Days Plus Late comings ded (Days)',type='integer'),
        'deducted_amount':fields.function(deducted_amoun, method=True, string='Deducted Amount',type='integer'),
    }
    _defaults = {
                 'absentees_this_month':0,
                 'approved_leaves_this_month':0
    }


class hr_biometric_device(osv.osv):
    _name = "hr.biometirc.device"
    _description = "Biometric Devices"

    _columns = {
        'name': fields.datetime('Date', required=True, select=1),
        'campus_name': fields.char('Reg No on Device'),
        'device_id': fields.char('ID'),
        'location_within_campus': fields.integer('Device ID'),
        'date_installed': fields.date("Date Installed", required=True, select=True),
        'provider': fields.char("Provider"),
        'company': fields.char("Company"),
        'support_contact':fields.char('Contact No:'),
        'attendance_history':fields.one2many('Attendance','device_odoo_config_id','hr.attendance')
    }
    _defaults = {
    }

class hr_device_pull_log(osv.osv):
    _name = "hr.device.pull.log"
    _description = "Biometric Devices"

    _columns = {
        'device_id': fields.char('ID'),
        'puncing_date_time': fields.char('Reg No on Device'),
        'em_empleado_acc_id': fields.char('Reg No on Device'),
        'status': fields.char('Reg No on Device'),
        'date_time_pulled': fields.char("Provider"),
        'pulled_by': fields.char("Company"),
    }
    _defaults = {
    }

class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    _description = "Employee"

    def _current_employee(self, cr, uid, ids):
        
        return True

    _columns = {
        'employee_attendance_ids': fields.one2many('hr.employee.attendance', 'employee_id','Employee Attendance Record'),
        'emp_regno_on_device': fields.char('Reg No on Device'),
        'empleado_account_id': fields.char('Empleado Acc ID'),
        'default_devicee_id': fields.char('Default Device'),
    }
    _defaults = {
    }
hr_employee()


class hr_employee_attendance(osv.osv):
    _name = "hr.employee.attendance"
    _description = "Employee Attendance"
    
    def on_change_month(self, cr, uid, ids, monthName):
        result = 0
        result = self.search(cr, uid, [()('attendance_month','=',str(monthName))])
  
   
   
    def get_late_arrival(self, cr, uid,ids, name, args, context=None):
        result = {}
        lat_min=0
        for f in self.browse(cr, uid, ids, context=context):
            print"employee id ",f.employee_id
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            print"Employee attendance day",day
            print"Employee attendance day name",day
            
            
            schedule_id_lst = []
           
            sch_detail_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('employee_id','=',f.employee_id.id),('dayofweek','=',day)])
            print "found sechde on this day ",sch_detail_ids
            if sch_detail_ids:
                sch_detail__objs = self.pool.get('hr.schedule.detail').browse(cr,uid, sch_detail_ids[0])
                att_time = datetime.strptime(sch_detail__objs.date_start,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                print"employee id ",f.employee_id.name
                print "attendance date:",f.attendance_date
                print "record id:",sch_detail__objs.id
                print"time sign in",f.sign_in
                FMT = '%H:%M:%S'
                print"schedule time",att_time
                #lat_min = datetime.strptime(f.sign_in, FMT) - datetime.strptime(att_time, FMT)
                
                timedelta = datetime.strptime(f.sign_in, FMT) - datetime.strptime(att_time, FMT)
                lat_min = timedelta.days + float(timedelta.seconds) / 60
                print "***************** late munites",lat_min
#             
            result[f.id] = lat_min
        return result 
    def total_short_minutes(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.late_early_arrival + f.early_late_going
        return result 
   

    
    def get_early_late_going(self, cr, uid,ids, name, args, context=None):
        result = {}
        early_minutes=0
        for f in self.browse(cr, uid, ids, context=context):

            print"employee id ",f.employee_id
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            print"Employee attendance day",day
            print"Employee attendance day name",day
            
            
            schedule_id_lst = []
           
            sch_detail_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('employee_id','=',f.employee_id.id),('dayofweek','=',day)])
            print "found sechde on this day ",sch_detail_ids
            if sch_detail_ids:
                sch_detail__objs = self.pool.get('hr.schedule.detail').browse(cr,uid, sch_detail_ids[0])
                att_time = datetime.strptime(sch_detail__objs.date_end,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                print"employee id ",f.employee_id.name
                print "attendance date:",f.attendance_date
                print "record id:",sch_detail__objs.id
                print"time sign in",f.sign_in
                FMT = '%H:%M:%S'
                print"schedule time",att_time
                #early_min = datetime.strptime(f.sign_out, FMT) - datetime.strptime(att_time, FMT)
                
                timedelta = datetime.strptime(f.sign_in, FMT) - datetime.strptime(att_time, FMT)
                early_minutes = timedelta.days + float(timedelta.seconds) / 60
                print "***************** late early_minutes",early_minutes
            result[f.id] = early_minutes

        return result 
    def get_day_ofweek(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            print"employee id ",f.employee_id
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            print"Employee attendance date",fdate.weekday()

        return result 
    
    
    def set_month(self):
        
        return True

    _columns = {
      'employee_id': fields.many2one('hr.employee'),
      'attendance_date': fields.date('Attendance Date'),
      'dayofweek': fields.function(get_day_ofweek, method=True, string='Day',type='selection', selection=DAYOFWEEK_SELECTION),
      'sign_in': fields.char('Sign In'),
      'sign_out': fields.char('Sign Out'),
      'late_early_arrival': fields.function(get_late_arrival, method=True, string='Late Arrival',type='integer'),
      'early_late_going': fields.function(get_early_late_going, method=True, string='Early Departure',type='integer'),
      'total_short_minutes': fields.function(total_short_minutes, method=True, string='Short Min ',type='integer'),
      'final_status': fields.selection([('Present', 'Present'),('Absent', 'Absent'),('Leave', 'Leave'),('Not-Out', 'Not-CheckOut')], 'Status'),
      'attendance_month': fields.char('Attendance Month'),
      'invoiced': fields.boolean('Invoiced',readonly = 1)
    }
    _defaults = {
        
    }
hr_employee()


class hr_attendance(osv.osv):
    _name = "hr.attendance"
    _inherit = "hr.attendance"
    _description = "Attendance"

    _columns = {
        'status':fields.char('Status'),
        'attendance_date':fields.date('Attendance Date'),
        'attendance_time':fields.char('Attendance Time'),
        'emp_regno_on_device': fields.char('Reg No on Device'),
        'empleado_account_id': fields.char('Empleado Acc ID'),
        'device_odoo_config_id': fields.many2one('hr.biometirc.device', "Odoo Device Parent"),
    }
    _defaults = {
    }
    
    
class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    def send_to_archieve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = "hr.payslip"
    _columns = {
    'state': fields.selection([
            ('draft', 'Draft'),
            ('verify', 'Waiting'),
            ('done', 'Done'),
            ('cancel', 'Rejected'),
            ('archieved', 'Archieved'),
        ], 'Status', select=True, readonly=True,
            help='* When the payslip is created the status is \'Draft\'.\
            \n* If the payslip is under verification, the status is \'Waiting\'. \
            \n* If the payslip is confirmed then status is set to \'Done\'.\
            \n* When user cancel payslip the status is \'Rejected\'.'),
      'salary_month':fields.char('Salary Month')# e.g 10-2017 also add this in search filter
                 }
    
    
    
    
    
    
    
        