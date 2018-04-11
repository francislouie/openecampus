import time
import datetime
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
# from dbus.decorators import method
import calendar
from pdftools.pdfdefs import false
#from samba.netcmd import domain

DAYOFWEEK_SELECTION = [('0', 'Monday'),
                       ('1', 'Tuesday'),
                       ('2', 'Wednesday'),
                       ('3', 'Thursday'),
                       ('4', 'Friday'),
                       ('5', 'Saturday'),
                       ('6', 'Sunday'),]

class res_company(osv.osv):
    
    """This object inherits res company adds fields related to accounts ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
                'empleado_branch_id':fields.char('Branch ID')
                }

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    _description = 'Contract'
    
    def deduct_amount(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if f.deduction_choice == 'auto':
                mss = self.pool.get('hr.monthly.attendance.calculation').search(cr, uid, [('contract_id','=', f.id),('is_invoiced','=', False)])
                print"mss",mss
                if mss:
                    rec = self.pool.get('hr.monthly.attendance.calculation').browse(cr,uid,mss[0]) 
                    deducted_amount = rec.final_deduced_amount 
                    result[f.id] = deducted_amount 
                else:
                    result[f.id] = 0.0
            else:
                deducted_amount = f.punched_deduction  
                result[f.id] = deducted_amount 
        return result
    
    def deduct_amount_month(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            mss = self.pool.get('hr.monthly.attendance.calculation').search(cr, uid, [('contract_id','=', f.id),('is_invoiced','=', False)])
            if mss:
                rec = self.pool.get('hr.monthly.attendance.calculation').browse(cr,uid,mss[0]) 
                cur_cal_month = rec.name
                result[f.id] = cur_cal_month 
            else:
                result[f.id] = 'Invoiced'
        return result
    _columns = {
        'attendance_calc': fields.one2many('hr.monthly.attendance.calculation','contract_id', "Attendance Calc"),
        'month': fields.function(deduct_amount_month, method=True, string='Month (e.g 02-2018)',type='char'),
        'punched_deduction':fields.integer('Punch to Deduct'),
        'deduction_choice':fields.selection([('manual','Manual Deduction'),('auto','Calculate from Attendance')],'Deduction Type'),
        'amount_to_deduct':fields.function(deduct_amount, method=True, string='Deducted Amount',type='float'),
    }


class hr_monthly_attendance_calculation(osv.osv):
    _name = "hr.monthly.attendance.calculation"
    _description = "Salary Calculation"
    
#     def get_twentry_m_late(self, cr, uid,ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             records = 0
#             t20_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>','2018-02-01'),('attendance_date','<','2018-02-28')])
#             if t20_ids:
#                 rect20 = self.pool.get('hr.employee.attendance').browse(cr,uid,t20_ids)
#                 for t20 in rect20:
#                     late_m = t20.total_short_minutes
#                     if late_m >=20 and late_m <30:
#                         records = records +1
#         result[f.id] = records
#         return result
    
    def get_decuction_twentry_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_late = f.twenty_minutes_late or 0
            if total_late >=3:
                day_ded = int(total_late/3)
            else:
                day_ded = 0
            
            result[f.id] = day_ded
            print"result",result
        return result
    
    def get_deducted_amount_on_half_days(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_half_days = f.half_days or 0
            salary = f.contract_id.wage or 0
            per_day = salary/30
            if per_day > 0:
                half_day_rate = per_day/2
            else:
                half_day_rate = 0
            
            deducted_amount = half_day_rate * total_half_days
            
            result[f.id] = deducted_amount
        return result
    
#     def get_half_days(self, cr, uid,ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             total_late = f.twenty_minutes_late or 0
#             if total_late >=3:
#                 day_ded = int(total_late/3)
#             else:
#                 day_ded = 0
#             
#             result[f.id] = day_ded
#             print"result",result
#         return result
    
    
#     def get_thirty_m_late(self, cr, uid,ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             records = 0
#             t20_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>','2018-02-01'),('attendance_date','<','2018-02-28')])
#             if t20_ids:
#                 rect20 = self.pool.get('hr.employee.attendance').browse(cr,uid,t20_ids)
#                 for t20 in rect20:
#                     late_m = t20.total_short_minutes
#                     if late_m >=30:
#                         records = records +1
#             result[f.id] = records
#         return result
    
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
            net= f.deduction_on_twenty_minutes_late + f.deduction_on_thirty_minutes_late  + f.net_absentees 

            if net <0:
                net = 0
            result[f.id] = net
        return result
#     def cur_cal_month(self, cr, uid,ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             print"calendar month",f.calendar_month
#             result[f.id] = f.name
#         return result
#     
    
    def final_deducted_amount(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            deduction_half_days = f.amount_deducted_half_days or 0
            deduction_absentees = f.amount_deducted_absentees
            final_deduction = deduction_half_days + deduction_absentees 
            result[f.id] = final_deduction
        return result
    
    def get_deducted_amount_on_absentees(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            final_deducted_days= f.deducted_absentees_plus_late_comings
            salary = f.contract_id.wage or 0
            per_day = salary/30
            total_deductions = per_day * final_deducted_days 
            #Also Hlaf days deductions
            result[f.id] = total_deductions
        return result
    
    def get_remarks(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            final_deducted_days= f.deducted_absentees_plus_late_comings
            salary = f.contract_id.wage or 0
            per_day = salary/30
            if per_day >0:
                half_day = per_day/2
            else:
                half_day = 0
            result[f.id] = "Per Day salary = "+str(per_day)+", Half Day Salary = "+str(half_day)
        return result
    
       
    _columns = {
        'calendar_month': fields.date('Month', required=True),
        'name': fields.char('Month Year'),
        'contract_id': fields.many2one('hr.contract'),
        'employee_id': fields.many2one('hr.employee'),
        'remarks': fields.function(get_remarks, method=True, string='Remarks',type='char'),
        'twenty_minutes_late':fields.integer('Twenty Minutes late'),
        'thirty_minutes_late':fields.integer('Thirty_minutes_late'),
        #'twenty_minutes_late': fields.function(get_twentry_m_late, method=True, string='Twenty Minutes late',type='integer'),
        'deduction_on_twenty_minutes_late': fields.function(get_decuction_twentry_m_late, method=True, string='Deduction (Days) On 20min',type='integer'),
        #'thirty_minutes_late': fields.function(get_thirty_m_late, method=True, string='Thirty Minutes late',type='integer'),

        'deduction_on_thirty_minutes_late': fields.function(get_decuction_thirty_m_late, method=True, string='Deduction (Days) On 30min',type='integer'),
        'half_days': fields.integer('No. of Half Days'),
        'amount_deducted_half_days': fields.function(get_deducted_amount_on_half_days, method=True, string='Deduction On Half Days',type='integer'),
        'absentees_this_month': fields.integer('Absentees This month'),
        'amount_deducted_absentees': fields.function(get_deducted_amount_on_absentees, method=True, string='Deduction On Absentees',type='integer'),
        'approved_leaves_this_month': fields.integer('Leaves This month'),
        'net_absentees': fields.function(get_absentess_leave, method=True, string='Absentees After Leave',type='integer'),
        'deducted_absentees_plus_late_comings': fields.function(absentess_plus_late_days, method=True, string='Absent Days Plus Late comings ded (Days)',type='integer'),
        'final_deduced_amount':fields.function(final_deducted_amount, method=True, string='Final Deducted Amount',type='integer'),
#         'cur_cal_month':fields.function(cur_cal_month, method=True,type='char'),
        'is_invoiced':fields.boolean('is invoiced'),
    }
    _defaults = {
                 'absentees_this_month':0,
                 'approved_leaves_this_month':0,
                 'is_invoiced':False
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
        'status': fields.char('Status'),
        'date_time_pulled': fields.char('Date time Pulled'),
        'pulled_by': fields.char('Pulled By'),
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
        'punch_attendance':fields.selection([('yes','Yes'),('no','No')],'Attendance Punching Allowed ?')
    }
    _defaults = {
        'punch_attendance': 'yes'
    }
hr_employee()


class hr_employee_attendance(osv.osv):
    _name = "hr.employee.attendance"
    _order = "attendance_date desc" 
    _description = "Employee Attendance"
    
    def on_change_month(self, cr, uid, ids, monthName):
        
        result = 0
        result = self.search(cr, uid, [()('attendance_month','=',str(monthName))])
  
   
   
    def get_late_arrival(self, cr, uid,ids, name, args, context=None):
        result = {}
        FMT = '%H:%M:%S'
        lat_min=0
        print"************************************late_arrival start********************************************"
        for f in self.browse(cr, uid, ids, context=context):
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            print "this day",day
          
            sch_detail_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('employee_id','=',f.employee_id.id),('dayofweek','=',str(day))])
            if sch_detail_ids:
                sch_detail__objs = self.pool.get('hr.schedule.detail').browse(cr,uid, sch_detail_ids[0])
                attendance_time =self.pool.get('hr.schedule').convert_datetime_timezone(sch_detail__objs.date_start, "UTC", "Asia/Karachi")
#                 attendance_time =sch_detail__objs.date_start
                schedule_signin = datetime.strptime(attendance_time,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                print"employee id ",f.employee_id.name
                print "attendance date:",f.attendance_date
                print"time sign in on",f.sign_in

                print"schedule sign in time",schedule_signin
             
                if f.sign_in and schedule_signin:
                    timedelta = datetime.strptime(f.sign_in, FMT) - datetime.strptime(schedule_signin, FMT)
                    if(datetime.strptime(f.sign_in, FMT) < datetime.strptime(schedule_signin, FMT)):
                        lat_min=0
                    else:
                        lat_min = timedelta.days + float(timedelta.seconds) / 60
                    print "***************** late munites",lat_min
                else:
                    lat_min=0
            
            else:
                lat_min=-10000
         
            result[f.id] = lat_min

        return result 
    def total_short_minutes(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if(f.final_status=='Status Not Clear'):
                print"Status Not Clear "
                result[f.id]=0
            else:    
                result[f.id] = f.late_early_arrival + f.early_late_going
        return result 
   

    
    def get_early_leaving(self, cr, uid,ids, name, args, context=None):
        print "***************** Early Going start*************************"
        result = {}
        FMT = '%H:%M:%S'
        early_minutes=0
        for f in self.browse(cr, uid, ids, context=context):
          
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            
            sch_detail_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('employee_id','=',f.employee_id.id),('dayofweek','=',str(day))])
            print "found sechdule on this day ",sch_detail_ids
            print "Schedule on date ",fdate
            if sch_detail_ids:
                sch_detail__objs = self.pool.get('hr.schedule.detail').browse(cr,uid, sch_detail_ids[0])
                print "****date end before conversion",sch_detail__objs.date_end
                attendance_time =self.pool.get('hr.schedule').convert_datetime_timezone(sch_detail__objs.date_end, "UTC", "Asia/Karachi")
#                 attendance_time =sch_detail__objs.date_end
                #schedule_time_signin_ = datetime.strptime(sch_detail__objs.date_start,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                schedule_time_signout_ = datetime.strptime(attendance_time,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                #print "schedule sign in time",schedule_time_signin_
                
#                 att_time = datetime.strptime(sch_detail__objs.date_end,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                print" ****employee sign out on: ",f.sign_out
                print "and schedule_time_signout",schedule_time_signout_
            
                #early_min = datetime.strptime(f.sign_out, FMT) - datetime.strptime(att_time, FMT)
                if f.sign_out =='00:00:00':
                    early_minutes=0
                else:
                    if f.sign_out and schedule_time_signout_:
                        timedelta = datetime.strptime(schedule_time_signout_, FMT) - datetime.strptime(f.sign_out, FMT)
                        if(datetime.strptime(schedule_time_signout_, FMT) < datetime.strptime(f.sign_out, FMT)):
                            early_minutes=0
                        else:
                            early_minutes = timedelta.days + float(timedelta.seconds) / 60
                            print "***************** Employee Left Earlly (in munutes)",early_minutes
                
                    else:
                        early_minutes=0
            else:
                early_minutes = -10000
            result[f.id] = early_minutes
        print "***************** Early Going End*************************"
        return result
    
    
    
     
    def get_day_ofweek(self, cr, uid,ids, name, args, context=None):
        result = {}
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        for f in self.browse(cr, uid, ids, context=context):
            print"employee id ",f.employee_id
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            name_day=days[day]
            result[f.id] = name_day.upper()
        return result 
    
    
    def set_month(self):
        return True

    _columns = {
      'employee_id': fields.many2one('hr.employee'),
      'attendance_date': fields.date('Date'),
      'dayofweek': fields.function(get_day_ofweek, method=True, string='Day',type='char'),
      'sign_in': fields.char('Sign In'),
      'sign_out': fields.char('Sign Out'),
      'late_early_arrival': fields.function(get_late_arrival, method=True, string='Late Arrival',type='integer'),
      'early_late_going': fields.function(get_early_leaving, method=True, string='Early Departure',type='integer'),
      'total_short_minutes': fields.function(total_short_minutes, method=True, string='Short Min ',type='integer'),
      'final_status': fields.selection([('Present', 'Present'),('Absent', 'Absent'),('Leave', 'Leave'),('public_holiday', 'Public Holiday'),('Holiday', 'Holiday'),('Not-Out', 'Not-CheckOut'),('Status Not Clear','Status Not Clear')], 'Status'),
      'attendance_month': fields.char('Attendance Month'),
      'invoiced': fields.boolean('Invoiced',readonly = 1)
    }
    _defaults = {
        
    }
hr_employee_attendance()


class hr_attendance(osv.osv):
    _name = "hr.attendance"
    _inherit = "hr.attendance"
    _description = "Attendance"

    _columns = {
        'employee_name': fields.char('Employee'),
        'status':fields.char('Status'),
        'attendance_date':fields.date('Attendance Date'),
        'attendance_time':fields.char('Attendance Time'),
        'emp_regno_on_device': fields.char('Reg No on Device'),
        'empleado_account_id': fields.char('Empleado Acc ID'),
        'device_odoo_config_id': fields.many2one('hr.biometirc.device', "Odoo Device Parent"),
    }
    _defaults = {
    }
    
    
class hr_payslip_run(osv.osv):
    _name = "hr.payslip.run"
    _inherit = "hr.payslip.run"
    _description = "hr payslip run"

    _columns = {
 
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
    
    
    
    
    
    
    
        