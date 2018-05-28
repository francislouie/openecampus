from openerp.osv import fields, osv
import datetime
import xlwt
import locale
import calendar
from datetime import datetime
#from osv import osv
from reportlab.pdfgen import canvas
import sys
import subprocess
import time
import urllib
#import netifaces 
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from xml.etree import ElementTree
import os

class sms_pull_hr_machine_data(osv.osv_memory):

    
    # Display the Current Branch ID in wizard
    def _get_branch_id(self, cr, uid, ids):         
        rec_id = self.pool.get('res.users').search(cr, uid, [('id','=',uid)])
        rec_id = self.pool.get('res.company').search(cr, uid, [('id','=',rec_id)])
        if rec_id:
            rec = self.pool.get('res.company').browse(cr, uid, rec_id[0])
            branch_id = rec.empleado_branch_id

        return branch_id
    
    
    # Display all inactive employees in wizard
    def _get_inactive_employees(self, cr, uid, ids): 
        inactive_employees = ''        
        inactive_recs = self.pool.get('hr.employee').search(cr, uid, [('isactive','=',False),('left_out','=',False),('punch_attendance','=','yes')])
        if inactive_recs:
            for id in inactive_recs:
                rec = self.pool.get('hr.employee').browse(cr, uid, id)
                inactive_employees += rec.name_related + ', '

        return inactive_employees
    
    
    # Display all employees with missing Empleado Ids in wizard
    def _get_missing_empleado_employees(self, cr, uid, ids): 
        empleado_missing_employees = ''        
        empleado_recs = self.pool.get('hr.employee').search(cr, uid, [('empleado_account_id','=', None),('punch_attendance','=','yes')])
        if empleado_recs:
            for id in empleado_recs:
                rec = self.pool.get('hr.employee').browse(cr, uid, id)
                empleado_missing_employees += rec.name_related + ', '

        return empleado_missing_employees
    
    
    # Display all employees with missing Contract Ids or missing wage in wizard
    def _get_missing_contract_employees(self, cr, uid, ids): 
        missing_contract_employees = ''        
        contract_recs = self.pool.get('hr.employee').search(cr, uid, [('contract_id','=', None), ('punch_attendance','=','yes')])
        if contract_recs:
            for id in contract_recs:
                rec = self.pool.get('hr.employee').browse(cr, uid, id)
                missing_contract_employees += rec.name_related + ', '
       
        contract_recs = self.pool.get('hr.contract').search(cr, uid, [('wage','=', 0)])
        if contract_recs:
            for id in contract_recs:
                rec = self.pool.get('hr.contract').browse(cr, uid, id)
                emp = self.pool.get('hr.employee').browse(cr, uid, rec.employee_id.id)
                missing_contract_employees += emp.name_related + ', '
        return missing_contract_employees
    
    
    # Display all employees with missing Department Ids in wizard
    def _get_missing_department_employees(self, cr, uid, ids): 
        missing_department_employees = ''        
        department_recs = self.pool.get('hr.employee').search(cr, uid, [('department_id','=', None), ('punch_attendance','=','yes')])
        if department_recs:
            for id in department_recs:
                rec = self.pool.get('hr.employee').browse(cr, uid, id)
                missing_department_employees += rec.name_related + ', '

        return missing_department_employees
    
    
    
    # Display all Departments with missing Schedules in wizard
    def _get_department_missing_schedules(self, cr, uid, ids): 
        departments = ''
        deptt_ids = self.pool.get('hr.department').search(cr, uid, [])
        if deptt_ids:
            for id in deptt_ids:
                schdle_id = self.pool.get('hr.schedule').search(cr, uid, [('department_id','=',id)])
                if not schdle_id:
                    rec = self.pool.get('hr.department').browse(cr, uid, id)
                    departments += rec.name + ', '

        return departments
    
    
    
    # Display the last pull date and time in wizard
    def _get_last_pull(self, cr, uid, ids):
        last_pull_date = None 
        pull_ids = self.pool.get('hr.device.pull.log').search(cr, uid, [])
        if pull_ids:
            last_id = pull_ids and max(pull_ids)
            rec = self.pool.get('hr.device.pull.log').browse(cr, uid, last_id)
            last_pull_date = str(datetime.strptime(rec.date_time_pulled,'%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S'))
        return last_pull_date
    
    
    
    
    # Display all employees with Attendance Punching Allowed ? set to Yes in Public Information of Employee
    def _get_exempted_employees(self, cr, uid, ids): 
        exempted_employees = ''        
        exempted_recs = self.pool.get('hr.employee').search(cr, uid, [('punch_attendance','=','no')])
        if exempted_recs:
            for _id in exempted_recs:
                rec = self.pool.get('hr.employee').browse(cr, uid, _id)
                exempted_employees += rec.name_related + ', '

        return exempted_employees
    
    
    
    
    
    _name = "sms.pull.hr.machine.data"
    _description = "Pull Data"
    _columns = {
              'pull_for_device': fields.selection([('all','Pull For All Device')],'Device'),
              'month': fields.date('Month to Get Absentees'),
              'month_comp': fields.date('Month For computing absentees'),
              'fetch_all_records': fields.boolean('Get All Previous Records'),
              'exempted_attendance': fields.text('Exempted from Biometric Attendance'),
              'inactive_employees': fields.text('Inactive Employees'),
              'missing_empleado': fields.text('Employees with Missing Empleado IDs'),
              'branch_id': fields.char(string='Current Branch ID'),
              'department_not_set': fields.text('Employees with Missing Departments'),
              'missing_contract': fields.text('Missing Contracts / Zero Wage'),
              'schedules_not_set': fields.text('Departments with Missing Schedules'),
              'last_pull': fields.char('Last Pull Date')
              }
    
    _defaults = {
        'branch_id':_get_branch_id,
        'inactive_employees':_get_inactive_employees,
        'missing_empleado':_get_missing_empleado_employees,
        'department_not_set':_get_missing_department_employees,
        'missing_contract': _get_missing_contract_employees,
        'schedules_not_set':_get_department_missing_schedules,
        'last_pull':_get_last_pull,
        'exempted_attendance': _get_exempted_employees,
                }
            
      
    def pull_attendance_device_data(self, cr, uid, ids, data):
        import requests
        import datetime, calendar
        

        
        # Check if Current Branch ID field is set in the wizard 
        branch_id = self.read(cr, uid, ids)[0]['branch_id']
        if not branch_id or branch_id == 0:
            raise osv.except_osv((),'No Branch ID Set, Cannot Proceed!')
        
        

        # Check if there are inactive employees in the wizard 
        inactive_id = self.read(cr, uid, ids)[0]['inactive_employees']
        if inactive_id:
            raise osv.except_osv((),'There are inactive employees in system, Cannot Proceed!')
            
            
        # Check if there are employees with missing empleado ids in the wizard 
        missing_empleado_id = self.read(cr, uid, ids)[0]['missing_empleado']
        if missing_empleado_id:
            raise osv.except_osv((),'Some employees have missing Empleado IDs, Cannot Proceed!')
         
         
        # Check if there are employees with missing contracts in the wizard 
#         missing_contract_id = self.read(cr, uid, ids)[0]['missing_contract']
#         if missing_contract_id:
#             raise osv.except_osv((),'Some employees have null or invalid contracts or wages undefined, Cannot Proceed!')
            
            
        # Check if there are employees with departments not assigned in the wizard 
        department_not_set_id = self.read(cr, uid, ids)[0]['department_not_set']
        if department_not_set_id:
            raise osv.except_osv((),'Some employees have not been assigned proper Departments, Cannot Proceed!')
            
            
        # Check if there are departments with no schedules in the wizard 
        schedules_not_set_id = self.read(cr, uid, ids)[0]['schedules_not_set']
        if schedules_not_set_id:
            raise osv.except_osv((),'Some departments are without schedules, Cannot Proceed!')
          
#          
#         # Check if Month is selected in the wizard
#         month_comp_date = self.read(cr, uid, ids)[0]['month_comp']
#         if not month_comp_date:
#             raise osv.except_osv((),'Date is required, Cannot Proceed!')
#         
#         
        # Assign value of Pull all previous record boolean to variable
        all_records = self.read(cr, uid, ids)[0]['fetch_all_records']
#         
#         
#         
        # Select branch id from res_company based on the currently logged in user from res_users
        company_query="""select empleado_branch_id from res_company where
            id=(select company_id from res_users where id="""+str(uid)+""" )"""
        
        cr.execute(company_query)
        branch_id=cr.fetchone()[0]
        print("-----branch id-------", str(branch_id))
        
        
        # check if records exists for every employee for the current month
        emp_ids = self.pool.get('hr.employee').search(cr,uid,[('isactive','=',True), ('punch_attendance','=','yes'), ('empleado_account_id','!=','')])
        
        current_date = datetime.datetime.today().strftime('%Y-%m-%d')
        salary_month = datetime.datetime.today().strftime('%m-%Y')
        current_month_name = datetime.datetime.today().strftime('%B')
        year = int(datetime.datetime.strptime(str(current_date), '%Y-%m-%d').strftime('%Y'))
        month = int(datetime.datetime.strptime(str(current_date), '%Y-%m-%d').strftime('%m'))

        num_days = calendar.monthrange(year, month)[1]
        current_month_dates = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        
        for emp_id in emp_ids:
            attendance_exists = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp_id),('attendance_date','=',current_date)])
        
            # if records don't exist then create records for each employee in employee attendance for the this current month
            if not attendance_exists:
                for date in current_month_dates:
                                        date_stamp = date.strftime('%Y%m%d')
                                        self.pool.get('hr.employee.attendance').create(cr, uid, {'employee_id': emp_id,'attendance_date': date_stamp, 
                                            'sign_in': '','sign_out': '','attendance_month': str(current_month_name)})
        
        
            # create an entry against the current employee in the hr_monthly_attendance_calcualtion table
            contr_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',emp_id)])
            if contr_ids:
                    exists = self.pool.get('hr.monthly.attendance.calculation').search(cr,uid,[('employee_id','=',emp_id),('name','=',salary_month),('contract_id','=',contr_ids[0])]) 
                      
                    if not exists:
                        self.pool.get('hr.monthly.attendance.calculation').create(cr,uid,{'employee_id':emp_id,'contract_id':contr_ids[0],'calendar_month':current_date,'name':salary_month,'absentees_this_month':0})
        
        
        # API REQUESTS STARTING NOW
        
        # Fetch all records if all previous records checkbox is selected
         
        if all_records:
            ack = requests.get('http://api.smilesn.com/attendance_pull.php?operation=acknowledge&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id='+str(branch_id)+'&ack_id=0')
              
        emp_id = []
        dates = []
        times = []
        item2 = 0
        status = 'ok'
        device_id = ''
                      
        while status == 'ok':
            item = 0
            # Development API
#             r = requests.get('http://api.smilesn.com/empleado/test_attendance.php?org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id=24')
            # Production API
            r = requests.get('http://api.smilesn.com/attendance_pull.php?operation=pull_attendance&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id='+str(branch_id))
            if(r.status_code == 200):
 
                read = r.json()
                print'----------- RAW DATA ------------------',read
                if(read['status']=='ok'):
                    ack_id = read['acknowledge_id']
                    ack = requests.get('http://api.smilesn.com/attendance_pull.php?operation=acknowledge&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id='+str(branch_id)+'&ack_id='+str(ack_id)) 
#                     print "---------------------------     json response    -----------------------------",read,ack
                    for att_record in read['att_records']:
                        device_id = att_record['device_id']
                        att_value = att_record['att_time']
                        att_date = datetime.datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                        att_value = att_record['att_time']
                        att_time = datetime.datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H%M%S')
                        if att_record['user_empleado_id'] not in emp_id:
                            emp_id.append(att_record['user_empleado_id'])
                        if att_date not in dates:
                            dates.append(att_date)
                        if att_time not in dates:
                            times.append(att_time)
             
                    while item < len(emp_id):
                        employee_id = self.pool.get('hr.employee').search(cr,uid,[('empleado_account_id','=',str(emp_id[item]))])
                        employee_rec = self.pool.get('hr.employee').browse(cr,uid,employee_id)
                        if employee_rec:
#                             print "----------    Data of user with ID   ---------------------",employee_rec[0].name_related
                            for att_records in read['att_records']: 
                                if att_records['user_empleado_id'] == emp_id[item]:
                     
                                    att_value = att_records['att_time']           
                                    biometric_id = att_records['bio_id']
                                    user_id = att_records['user_empleado_id']
                                    device_id = att_records['device_id']         
                                    date_stamp = datetime.datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                                    time_stamp = datetime.datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H:%M:%S')
                                     
                                    for date in dates:
                                        if date_stamp == date:
                                            search_rec = self.pool.get('hr.attendance').search(cr,uid,[('employee_id','=',employee_rec[0].id),('attendance_date','=',date_stamp),('attendance_time','=',time_stamp)])   
                                            if not search_rec:
                                                result = self.pool.get('hr.attendance').create(cr, uid, {
                                                'attendance_date': date_stamp,
                                                'attendance_time': time_stamp,                            
                                                'status': 'Sign In',
                                                'action':'sign_in',
                                                'name': '2018-01-11 07:45:23',
                                                'empleado_account_id': user_id, 
                                                'emp_regno_on_device': biometric_id,
                                                'employee_name': employee_rec[0].name_related
                                                })  
#                                                   
                        item += 1
   
            status = read['status']
         
        # Logging functionality on successful Pull
        if status == '0':
 
            time_detail = datetime.datetime.now()
            rec_id = self.pool.get('res.users').search(cr, uid, [('id','=',uid)])
            user = self.pool.get('res.users').browse(cr, uid, rec_id[0])
             
            self.pool.get('hr.device.pull.log').create(cr, uid, {
                'device_id': device_id,
                'status': 'success',
                'date_time_pulled': time_detail,
                'pulled_by': user.login,
            })                          
            print'---- pull date logged ----'             
 
        return True    

sms_pull_hr_machine_data()










































# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: