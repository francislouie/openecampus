import time
import datetime
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dbus.decorators import method
#from samba.netcmd import domain

class res_company(osv.osv):
    
    """This object inherits res company adds fields related to accounts ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
                'empleado_branch_id':fields.char('Branch ID')
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
  
   
   
    def get_late_early_arrival(self, cr, uid,ids, name, args, context=None):
        result = {}
        vari=0
        for f in self.browse(cr, uid, ids, context=context):
            print"employee id ",f.employee_id
            print"Employee attendance date",f.attendance_date
            
            
            schedule_id_lst = []
           
            sch_detail_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('employee_id','=',f.employee_id.id),('day','=',str(f.attendance_date))])
            if sch_detail_ids:
                sch_detail__objs = self.pool.get('hr.schedule.detail').browse(cr,uid, sch_detail_ids)
                att_time = datetime.strptime(sch_detail__objs[0]['date_start'],"%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                print"time from ffff",f.sign_in
                FMT = '%H:%M:%S'
                print"time from datetime",att_time
                # tdelta = datetime.strptime(f.sign_in, FMT) - datetime.strptime(att_time, FMT)
#             
            result[f.id] = 0
        return result 
    def total_late(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
#              sql = """SELECT COALESCE(count(id),'0') from sms_student
#                       WHERE current_class = """+str(f.academic_cal_id.id)+""" AND fee_type = """+str(f.fee_structure_id.id)
#              cr.execute(sql)
#              row = cr.fetchone()
             result[f.id] = 43
        return result 
   

    
    def get_early_late_going(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = 90
        return result 
    
    
    
    def set_month(self):
        return True

    _columns = {
        'employee_id': fields.many2one('hr.employee'),
      'attendance_date': fields.date('Attendance Date'),
      'sign_in': fields.char('Sign In'),
      'sign_out': fields.char('Sign Out'),
      'late_early_arrival': fields.char('Late Arrival'),
      'early_late_going': fields.char('Early Departure'),
      'late_early_arrival': fields.function(get_late_early_arrival, method=True, string='Late Arrival',type='integer'),
      'early_late_going': fields.function(get_early_late_going, method=True, string='Early Departure',type='integer'),
      'total_late': fields.function(total_late, method=True, string='Total Late ',type='integer'),
      'final_status': fields.selection([('Present', 'Present'),('Absent', 'Absent'),('Leave', 'Leave')], 'Attendance Status'),
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
    
    
    
    
    
    
    
        