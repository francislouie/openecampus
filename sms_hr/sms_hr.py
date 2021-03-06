import time
import datetime
from datetime import datetime, timedelta 
from openerp.osv import fields, osv
from openerp.tools.translate import _
# from dbus.decorators import method
import calendar
from pdftools.pdfdefs import false
# from matplotlib.legend_handler import update_from_first_child
#from samba.netcmd import domain

DAYOFWEEK_SELECTION = [('0', 'Monday'),
                       ('1', 'Tuesday'),
                       ('2', 'Wednesday'),
                       ('3', 'Thursday'),
                       ('4', 'Friday'),
                       ('5', 'Saturday'),
                       ('6', 'Sunday'),]

ATTENDANCE_STATUS_LIST = [('Present', 'Present'),('Absent', 'Absent'),('Leave', 'Leave'),('public_holiday', 'Public Holiday'),('Holiday', 'Holiday'),('Status Not Clear','Status Not Clear'),('Unknown','Unknown')]


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
    
    def get_decuction_twentry_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_20_late = f.twenty_minutes_late or 0
            total_30_late = f.thirty_minutes_late or 0
            if total_20_late >=2:
                day_ded = int(total_20_late/3)
                remainder_20 = total_20_late % 3
                remainder_30 = total_30_late % 2
                if remainder_20 == 2 and remainder_30 == 1:
                    day_ded += 1
            else:
                day_ded = 0
            
            result[f.id] = day_ded
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


    def get_half_days(self, cr, uid,ids, name, args, context=None):
        result = {}
        half_day_count = 0
        for f in self.browse(cr, uid, ids, context=context):
            month_name = datetime.strptime(f.name, '%m-%Y').strftime('%B')
            emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_month','=',month_name)]) 
            if emp_att_ids:
                for emp in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                    if emp.sign_in != '00:00:00' and emp.sign_in == emp.sign_out:
                        half_day_count += 1          
            result[f.id] = half_day_count
        return result


    def get_twentry_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            month_comp_date =f.calendar_month
            year = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%Y'))
            mont = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%m'))
            if(mont <10):
                month ='0'+str(mont)
            else:
                month =''+str(mont) 
            mon_days = calendar.monthrange(year,mont)[1]
            date_from =str(str(year)+'-'+str(month)+'-01')
            date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))
       
            
            twenty_minutes_late=0
            emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>=',date_from),('attendance_date','<=',date_to)]) 
            for emp in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                if(emp.total_short_minutes >=20 and  emp.total_short_minutes< 30) and emp.final_status != ATTENDANCE_STATUS_LIST[5][0]:
                    twenty_minutes_late=twenty_minutes_late+1
            result[f.id] = twenty_minutes_late
        return result
    
    def get_thirty_m_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            month_comp_date =f.calendar_month
            year = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%Y'))
            mont = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%m'))
            if(mont <10):
                month ='0'+str(mont)
            else:
                month =''+str(mont) 
            mon_days = calendar.monthrange(year,mont)[1]
            date_from =str(str(year)+'-'+str(month)+'-01')
            date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))

            print"Employee id",f.employee_id.id
            thirty_minutes_late=0
            emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_date','>=',date_from),('attendance_date','<=',date_to)]) 
            for emp in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                if(emp.total_short_minutes >= 30 and emp.final_status != ATTENDANCE_STATUS_LIST[5][0]):
                    thirty_minutes_late=thirty_minutes_late+1
            result[f.id] = thirty_minutes_late
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
            print' --- net absentees this month ----', net
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
    
    def get_absentees_this_month(self, cr, uid, ids, name, args, context=None):
        result = {}
        absent_count = 0
        for f in self.browse(cr, uid, ids, context=context):
            month_name = datetime.strptime(f.name, '%m-%Y').strftime('%B')
            emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',f.employee_id.id),('attendance_month','=',month_name)]) 
            if emp_att_ids:
                for emp in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                    if emp.final_status =='Absent':
                        absent_count += 1
                        
            result[f.id] = absent_count
        return result
    
    
    def get_unknown_status(self, cr, uid, emp_id, date_from, date_to, context=None):
        result = 0
        emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp_id),('attendance_date','>=',date_from),('attendance_date','<=',date_to)]) 
        if emp_att_ids:
            for emp in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                if emp.final_status == ATTENDANCE_STATUS_LIST[6][0]: 
                    result += 1
        return result  
    
     
    _columns = {
        'calendar_month': fields.date('Month', required=True),
        'name': fields.char('Month Year'),
        'contract_id': fields.many2one('hr.contract'),
        'employee_id': fields.many2one('hr.employee'),
        'remarks': fields.function(get_remarks, method=True, string='Remarks',type='char'),
        'half_days': fields.function(get_half_days, method=True, string='Half days',type='integer'),
        'twenty_minutes_late': fields.function(get_twentry_m_late, method=True, string='Twenty Minutes late',type='integer'),
        'deduction_on_twenty_minutes_late': fields.function(get_decuction_twentry_m_late, method=True, string='Deduction (Days) On 20min',type='integer'),
        'thirty_minutes_late': fields.function(get_thirty_m_late, method=True, string='Thirty Minutes late',type='integer'),
        'deduction_on_thirty_minutes_late': fields.function(get_decuction_thirty_m_late, method=True, string='Deduction (Days) On 30min',type='integer'),
        'amount_deducted_half_days': fields.function(get_deducted_amount_on_half_days, method=True, string='Deduction On Half Days',type='integer'),
        'absentees_this_month': fields.function(get_absentees_this_month, method=True, string='Absentees This month',type='integer'),
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
    
    def _get_schedule(self, cr, uid, ids, name, args, context=None):
        
        result = {}
        for f in self.browse(cr, uid, ids):
            name = self.pool.get('hr.employee.attendance').get_active_schedule(cr, uid, ids, f.id)
        result[f.id] = name
        return result

    _columns = {
        'employee_attendance_ids': fields.one2many('hr.employee.attendance', 'employee_id','Employee Attendance Record'),
        'emp_regno_on_device': fields.char('Reg No on Device'),
        'empleado_account_id': fields.char('Empleado Acc ID'),
        'default_devicee_id': fields.char('Default Device'),
        'punch_attendance':fields.selection([('yes','Yes'),('no','No')],'Attendance Punching Allowed ?'),
        'left_out': fields.boolean('Left Out'),
        'active_schedule': fields.function(_get_schedule, method=True, string='Active Schedule', type='char')
    }
    _defaults = {
        'punch_attendance': 'yes',
        'left_out': False
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
        emp_dep_id=0
        print"************************************late_arrival start********************************************"
        for f in self.browse(cr, uid, ids, context=context):
            fdate = datetime.strptime(f.attendance_date,'%Y-%m-%d')
            day = fdate.weekday()
            emp_dep_ids = self.pool.get('hr.employee').search(cr,uid, [('id','=',f.employee_id.id)])
            for emp in self.pool.get('hr.employee').browse(cr,uid, emp_dep_ids):
                if (emp.department_id):
                    emp_dep_id=emp.department_id.id
                else:
                    print"department is not assign"     
            sch_lines_ids = self.pool.get('hr.schedule.lines').search(cr,uid, [('department_id','=',emp_dep_id),('dayofweek','=',str(day)),('schedule_id','=',f.active_schedule_id)])
            if sch_lines_ids:
                sch_lines__objs = self.pool.get('hr.schedule.lines').browse(cr,uid, sch_lines_ids[0])
                attendance_time =self.pool.get('hr.schedule').convert_datetime_timezone(sch_lines__objs.date_start, "UTC", "Asia/Karachi")
                schedule_signin = datetime.strptime(attendance_time,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                if f.sign_in and schedule_signin:
                    timedelta = datetime.strptime(f.sign_in, FMT) - datetime.strptime(schedule_signin, FMT)
                    if(datetime.strptime(f.sign_in, FMT) < datetime.strptime(schedule_signin, FMT)):
                        lat_min=0
                    else:
                        lat_min = timedelta.days + float(timedelta.seconds) / 60
                else: 
                    lat_min=0
             
            else:
                lat_min=-10000
         
            result[f.id] = lat_min

        return result 
    def total_short_minutes(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if f.final_status== ATTENDANCE_STATUS_LIST[5][0]:
                print"Status Not Clear 1"
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
             
            emp_dep_ids = self.pool.get('hr.employee').search(cr,uid, [('id','=',f.employee_id.id)])
            for emp in self.pool.get('hr.employee').browse(cr,uid, emp_dep_ids):
                if (emp.department_id):
                    emp_dep_id=emp.department_id.id
                else:
                    print"department is not assign"     
            sch_lines_ids = self.pool.get('hr.schedule.lines').search(cr,uid, [('department_id','=',emp_dep_id),('dayofweek','=',str(day)),('schedule_id','=',f.active_schedule_id)])
            if sch_lines_ids:
                sch_detail__objs = self.pool.get('hr.schedule.lines').browse(cr,uid, sch_lines_ids[0])
                attendance_time =self.pool.get('hr.schedule').convert_datetime_timezone(sch_detail__objs.date_end, "UTC", "Asia/Karachi")
                schedule_time_signout_ = datetime.strptime(attendance_time,"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                if f.sign_out =='00:00:00':
                    early_minutes=0
                else:
                    if f.sign_out and schedule_time_signout_:
                        timedelta = datetime.strptime(schedule_time_signout_, FMT) - datetime.strptime(f.sign_out, FMT)
                        if(datetime.strptime(schedule_time_signout_, FMT) < datetime.strptime(f.sign_out, FMT)):
                            early_minutes=0
                        else:
                            early_minutes = timedelta.days + float(timedelta.seconds) / 60
                 
                    else:
                        early_minutes=0
            else:
                early_minutes = -10000
            result[f.id] = early_minutes
        print "***************** Early Going End*************************"
        return result
    
    def get_signin_time(self, cr, uid, ids, name, args, context=None):
        time = {}
        for f in self.browse(cr, uid, ids, context=context):
            employee_record = self.pool.get('hr.employee').browse(cr, uid, f.employee_id.id) 
            employee_ids = self.pool.get('hr.attendance').search(cr,uid, [('empleado_account_id','=',employee_record.empleado_account_id),('attendance_date', '=', f.attendance_date)])
            if employee_ids:
                recs_found = self.pool.get('hr.attendance').browse(cr,uid,employee_ids)
                emp_time_recs = sorted(recs_found, key=lambda k: k['attendance_time'])
                time[f.id] = emp_time_recs[0]['attendance_time']          
#                 time[f.id] = recs_found.attendance_time
            else:
                time[f.id] = '00:00:00'
        return time
    
    def get_signout_time(self, cr, uid, ids, name, args, context=None):
        time = {}
        for f in self.browse(cr, uid, ids, context=context):
            employee_record = self.pool.get('hr.employee').browse(cr, uid, f.employee_id.id) 
            employee_ids = self.pool.get('hr.attendance').search(cr,uid, [('empleado_account_id','=',employee_record.empleado_account_id),('attendance_date', '=', f.attendance_date)])
            if employee_ids:
                recs_found = self.pool.get('hr.attendance').browse(cr,uid,employee_ids)
                emp_time_recs = sorted(recs_found, key=lambda k: k['attendance_time'])
                time[f.id] = emp_time_recs[-1]['attendance_time']
            else:
                time[f.id] = '00:00:00'
        return time
    
    
    def get_final_status(self, cr, uid,ids, name, args, context=None):
        result = {}
        hr_holiday_rec = False
        for f in self.browse(cr, uid, ids, context=context):
            if f.sign_in == '00:00:00':
                final_status = ATTENDANCE_STATUS_LIST[6][0]
                current_date = datetime.strptime(f.attendance_date,'%Y-%m-%d')
                day = current_date.weekday()
                employee_record = self.pool.get('hr.employee').browse(cr, uid, f.employee_id.id) 
                hr_attendance_exists = self.pool.get('hr.attendance').search(cr,uid, [('empleado_account_id','=',employee_record.empleado_account_id),('attendance_date', '>=', f.attendance_date)])
                if hr_attendance_exists:
                    if f.employee_id.department_id:
                                emp_rec_ids = self.pool.get('hr.schedule').search(cr,uid,[('department_id','=',f.employee_id.department_id.id),('state','=','validate')]) 
                                if emp_rec_ids:
                                    for sche in self.pool.get('hr.schedule').browse(cr,uid, emp_rec_ids):
                                        if sche.public_holiday_ids:
                                            for puh in sche.public_holiday_ids:
                                                if puh.holiday_date == f.attendance_date:
                                                    hr_holiday_rec =True

                    if hr_holiday_rec:
                        final_status = ATTENDANCE_STATUS_LIST[3][0]             #Public Holiday
                        hr_holiday_rec = False
                    else:    
                        if(day==5 or day==6):
                            
                            final_status = ATTENDANCE_STATUS_LIST[4][0]         #Holiday
                        else:    
                            final_status = ATTENDANCE_STATUS_LIST[1][0]           #Absent
            else:
                if f.sign_in == f.sign_out:
                    final_status = ATTENDANCE_STATUS_LIST[5][0]                   #Status Not Clear
                    print'---------- status not clear hit -------------', final_status
                else:
                    final_status = ATTENDANCE_STATUS_LIST[0][0]                   #Present
                    
            result[f.id] = final_status
        return result 
    
    
    
    def _get_status_not_clear(self, cr, uid, ies, month, context=None):
        result = {}
        status_count = 0
        emp_ids = self.search(cr,uid,[('employee_id','=',ies),('attendance_month','=',month)])
        if emp_ids:
            for f in self.browse(cr, uid, emp_ids):
                if f.sign_in != '00:00:00' and f.sign_in == f.sign_out:
                    status_count += 1
                print'----- STATUS NOT CLEAR COUNT ----', status_count
            result = status_count    
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
    
    def get_active_schedule(self, cr, uid, ids, emp, context=None):
        rec_id = self.search(cr, uid, [('employee_id', '=', emp)], order='id desc', limit=1)
        if rec_id:
            rec_att = self.browse(cr, uid, rec_id[0])
            rec = self.pool.get('hr.schedule').browse(cr, uid, rec_att.active_schedule_id)
        result = rec.name
        return result
                
    _columns = {
      'employee_id': fields.many2one('hr.employee', string='Employee'),
      'attendance_date': fields.date('Date'),
      'dayofweek': fields.function(get_day_ofweek, method=True, string='Day',type='char'),
      'sign_in': fields.function(get_signin_time, method=True, string='Sign In',type='char'),
      'sign_out': fields.function(get_signout_time, method=True, string='Sign Out',type='char'),
      'late_early_arrival': fields.function(get_late_arrival, method=True, string='Late Arrival',type='integer'),
      'early_late_going': fields.function(get_early_leaving, method=True, string='Early Departure',type='integer'),
      'total_short_minutes': fields.function(total_short_minutes, method=True, string='Short Min ',type='integer'),
      'final_status': fields.function(get_final_status, string='Status',type='selection', selection=ATTENDANCE_STATUS_LIST),
      'attendance_month': fields.char('Attendance Month'),
      'invoiced': fields.boolean('Invoiced',readonly = 1),
      'active_schedule_id': fields.integer('Active Schedule Id'),
      'schedule_name': fields.function(get_active_schedule, method=True, type='char', string='Active Schedule')
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


    def create(self, cr, uid, vals, context=None):
        year = int(datetime.strptime(str(vals['date_start']), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.strptime(str(vals['date_start']), '%Y-%m-%d').strftime('%m'))
        if(mont <10):
            month ='0'+str(mont)
        else:
            month =''+str(mont) 
        mon_days = calendar.monthrange(year,mont)[1]
        date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))
        date_today = datetime.today().strftime('%Y-%m-%d')
        if (date_to > date_today):
            date_tto=date_today
        else:
            date_tto=date_to
        date = self.pool.get('sms.pull.hr.machine.data')._get_last_pull(cr, uid, vals)
        d= datetime.strptime(date,"%Y-%m-%d %H:%M:%S") + timedelta(hours=12)  
        pull_date =datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        date_today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        if  (date_today > pull_date):
            raise osv.except_osv(('First Pull attendance'),'')
        else:
            payslip_run_id = super(hr_payslip_run, self).create(cr, uid, vals, context=context)
            
            sql_query = """Update hr_payslip_run set date_end ='"""+str(date_tto)+"""' where id ="""+str(payslip_run_id)+""""""
            cr.execute(sql_query)
        return payslip_run_id



    def onchange_set_domain(self, cr, uid , ids, date_start,context=None):
        print"onchange_set_domain is called",date_start
        year = int(datetime.strptime(str(date_start), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.strptime(str(date_start), '%Y-%m-%d').strftime('%m'))
        if(mont <10):
            month ='0'+str(mont)
        else:
            month =''+str(mont) 
        mon_days = calendar.monthrange(year,mont)[1]
        date_from =str(str(year)+'-'+str(month)+'-01')
        date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))
        date_today = datetime.today().strftime('%Y-%m-%d')
        print"Date today ",date_today 
        print"Date from ",date_from 
      
        print"date to ",date_to
        
        if (date_to > date_today):
            date_tto=date_today
        else:
            date_tto=date_to
        return {'value': {'date_end':date_tto,'date_start':date_from}}

    def _get_last_pull(self, cr, uid, ids): 


        return self.pool.get('sms.pull.hr.machine.data')._get_last_pull(cr, uid, ids)

    

    _columns = {
   'last_pull':fields.date('Last Pull '),
    }
    _defaults = {
        'last_pull':_get_last_pull
    }
    
class hr_payslip(osv.osv):
    ''' Pay Slip (inprocess)'''
    def create(self, cr, uid, vals, context=None):
        date = self.pool.get('sms.pull.hr.machine.data')._get_last_pull(cr, uid, vals)
        d= datetime.strptime(date,"%Y-%m-%d %H:%M:%S") + timedelta(hours=12)  
        pull_date =datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        date_today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print'---- vals -----', vals
        print"pull date",pull_date
        print"today date",date_today
        year = int(datetime.strptime(str(vals['date_from']), '%Y-%m-%d').strftime('%Y'))
        month = int(datetime.strptime(str(vals['date_from']), '%Y-%m-%d').strftime('%m'))
        month_days = calendar.monthrange(year,month)[1]
        date_from = datetime.strptime(vals['date_from'], "%Y-%m-%d").strftime("%Y-%m-%d")
        date_to = datetime(year=int(year), month=int(month), day=int(month_days)).strftime("%Y-%m-%d")
        date_today = datetime.today().strftime('%Y-%m-%d')
        print"Date today ",date_today 
        print"Date from ",date_from 
      
        print"date to ",date_to
        
        if (date_to > date_today):
            date_tto=date_today
        else:
            date_tto=date_to
        print' --------- employee id for payslip -----------', vals['employee_id']
        print'--------- date from man ------', date_from
        print'--------- date to man ------', date_to
        
#         unknown = self.pool.get('hr.monthly.attendance.calculation').get_unknown_status(cr, uid, vals['employee_id'], date_from, date_to)
#         print' ---- unknown ---------', unknown
#          
#         if unknown > 0:
#             raise osv.except_osv(('Cannot Proceed'),'There are unknown statuses for this employee in the current month!')
        
        if  (date_today > pull_date):
        
            raise osv.except_osv(('First Pull attendance'),'')
        else:
            payslip_id = super(hr_payslip, self).create(cr, uid, vals, context=context)
            sql_query = """Update hr_payslip set date_to ='"""+str(date_tto)+"""' where id ="""+str(payslip_id)+""""""
            cr.execute(sql_query)
        return payslip_id
    
    def hr_verify_sheet(self, cr, uid, ids, context=None):
        
        super(hr_payslip, self).hr_verify_sheet(cr, uid, ids, context=context)
        
        
        
        obj = self.browse(cr, uid, ids, context=context)
        employee_id = obj[0].employee_id.id
        mont = datetime.strptime(str(obj[0].date_from), '%Y-%m-%d').strftime('%m')
        year = datetime.strptime(str(obj[0].date_from), '%Y-%m-%d').strftime('%Y')
        slip_month= mont +'-'+year
        print"before",employee_id
        hr_id = self.pool.get('hr.monthly.attendance.calculation').search(cr,uid,[('name','=',slip_month),('employee_id','=',employee_id)]) 
        print"After"
        monthly_att= self.pool.get('hr.monthly.attendance.calculation').write(cr, uid, hr_id, {'is_invoiced': True}, context=context)
        return monthly_att
    
    
   
    
    def onchange_set_domain(self, cr, uid , ids, date_from,context=None):
        print"onchange_set_domain is called",date_from
        year = int(datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%m'))
        if(mont <10):
            month ='0'+str(mont)
        else:
            month =''+str(mont) 
        mon_days = calendar.monthrange(year,mont)[1]
        date_from =str(str(year)+'-'+str(month)+'-01')
        date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))
        date_today = datetime.today().strftime('%Y-%m-%d')
        print"Date today ",date_today 
        print"Date from ",date_from 
      
        print"date to ",date_to
        
        if (date_to > date_today):
            date_tto=date_today
        else:
            date_tto=date_to
        return {'value': {'date_to':date_tto,'date_from':date_from}}
    
    
    
    
    def _get_last_pull(self, cr, uid, ids): 
        return self.pool.get('sms.pull.hr.machine.data')._get_last_pull(cr, uid, ids)
    
    
    
    
    
    
    def send_to_archieve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = "hr.payslip"
    _columns = {
        
        
    'last_pull':fields.date('Last Pull '),
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
    
    _defaults = {
                'date_from': lambda *a: time.strftime('%Y-%m-01'),
                'last_pull':_get_last_pull
                 
    }
    
    
    
    
    
        