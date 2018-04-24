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
        inactive_recs = self.pool.get('hr.employee').search(cr, uid, [('isactive','=',False),('punch_attendance','=','yes')])
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
              'schedules_not_set': fields.text('Departments with Missing Schedules'),
              'last_pull': fields.char('Last Pull Date')
              }
    
    _defaults = {
        'branch_id':_get_branch_id,
        'inactive_employees':_get_inactive_employees,
        'missing_empleado':_get_missing_empleado_employees,
        'department_not_set':_get_missing_department_employees,
        'schedules_not_set':_get_department_missing_schedules,
        'last_pull':_get_last_pull,
        'exempted_attendance': _get_exempted_employees,
                }
            
      
    def pull_attendance_device_data(self, cr, uid, ids, data):
        import requests
        
         
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
         
        # Check if there are employees with departments not assigned in the wizard 
        department_not_set_id = self.read(cr, uid, ids)[0]['department_not_set']
        if department_not_set_id:
            raise osv.except_osv((),'Some employees have not been assigned proper Departments, Cannot Proceed!')
         
         
        # Check if there are departments with no schedules in the wizard 
        schedules_not_set_id = self.read(cr, uid, ids)[0]['schedules_not_set']
        if schedules_not_set_id:
            raise osv.except_osv((),'Some departments are without schedules, Cannot Proceed!')
         
         
        # Check if Month is selected in the wizard
        month_comp_date = self.read(cr, uid, ids)[0]['month_comp']
        if not month_comp_date:
            raise osv.except_osv((),'Date is required!')
        
        
        # Assign value of Pull all previous record boolean to variable
        all_records = self.read(cr, uid, ids)[0]['fetch_all_records']
        
        
        
        # Select branch id from res_company based on the currently logged in user from res_users
        company_query="""select empleado_branch_id from res_company where
            id=(select company_id from res_users where id="""+str(uid)+""" )"""
       
        cr.execute(company_query)
        branch_id=cr.fetchone()[0]
        print("-----branch id-------", str(branch_id))
        
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

#                         print "empleado id",att_record['user_empleado_id']
                        if att_record['user_empleado_id'] not in emp_id:
                            emp_id.append(att_record['user_empleado_id'])
                                
                    for att_record in read['att_records']:
                        att_value = att_record['att_time']
                        att_date = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                        att_value = att_record['att_time']
                        att_time = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H%M%S')
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
                                    
                                    date_time_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')           
                                    date_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                                    time_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H:%M:%S')
                                    
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

            time_detail = datetime.now()
            rec_id = self.pool.get('res.users').search(cr, uid, [('id','=',uid)])
            user = self.pool.get('res.users').browse(cr, uid, rec_id[0])
            
            self.pool.get('hr.device.pull.log').create(cr, uid, {
                'device_id': device_id,
                'status': 'success',
                'date_time_pulled': time_detail,
                'pulled_by': user.login,
            })                          
                         


        while item2 < len(emp_id):
            employee_id = self.pool.get('hr.employee').search(cr,uid,[('empleado_account_id','=',str(emp_id[item2]))])
            employee_rec = self.pool.get('hr.employee').browse(cr,uid,employee_id) 
#                     print '-------------HR Employeee Table-------------'
            for date in dates:
#                             print "----------- All Dates -------------", date
                            search_rec1 = self.pool.get('hr.attendance').search(cr,uid,[('empleado_account_id','=',emp_id[item2]),('attendance_date', '=', date)])                                            
                            if search_rec1:
                                recs_found1 = self.pool.get('hr.attendance').browse(cr,uid,search_rec1) 
                                emp_time_recs = sorted(recs_found1, key=lambda k: k['attendance_time']) 
                                emptime_list = []
                                signin = True
                                for rec2 in emp_time_recs:
                                    emptime_list.append(rec2.attendance_time)
                                    if signin == True:
                                        result = self.pool.get('hr.attendance').write(cr, uid, rec2.id, {'status': 'Sign In'})
                                        signin = False
                                    else:
                                        result = self.pool.get('hr.attendance').write(cr, uid, rec2.id, {'status': 'Sign Out'}) 
                                        signin = True 
                              
                                if employee_rec:
#                                     print'------------- Dates for this employee -------------- ', date, ' ---- ',employee_rec[0].id   
                                    employee_date = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',employee_rec[0].id),('attendance_date','=',date)])
                                    if not employee_date:
                                        if(emptime_list[0] == emptime_list[-1]):
                                            f_status = 'Status Not Clear'
                                        else:
                                            f_status = 'Present'
                                        self.pool.get('hr.employee.attendance').create(cr, uid, {
                                            'employee_id': employee_rec[0].id,
                                            'attendance_date': date, 
                                            'sign_in': emptime_list[0],
                                            'sign_out': emptime_list[-1],
                                            'final_status': f_status,
                                            'attendance_month': str(datetime.strptime(date,'%Y%m%d').strftime('%B'))})
                                else:
                                    print " not found on ERP for emplead acc",employee_rec
         
            item2 += 1
            
        self.compute_attendance_absentees(cr, uid, ids, data)
        self.summaries_employee_attendance(cr, uid, ids, data)
        return True    
    
    def compute_attendance_absentees(self, cr, uid, ids, data):
        print "compute abesentee method called ..................."
        import datetime, calendar
        
        date_today = datetime.datetime.today().strftime('%Y%m%d')
        
        month_comp_date = self.read(cr, uid, ids)[0]['month_comp']
        if not month_comp_date:
            raise osv.except_osv((),'Date is required')
        year = int(datetime.datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%Y'))
        month = int(datetime.datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%m'))

        emp_id_list = []

        dates = []
        
        sqlr ="""SELECT * FROM hr_employee"""
        cr.execute(sqlr)
        rec_ids = cr.fetchall() 
        for record in rec_ids:
            emp_id_list.append(record[0])
        num_days = calendar.monthrange(year, month)[1]
        days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        
        for day in days:
            date_stamp = day.strftime('%Y%m%d')
            if date_stamp <= date_today:
                dates.append(date_stamp)
        print'------ Attendance Date List --------', dates    
        for date_item in dates:
                hr_holiday_rec = False
                
                for emp_idd in emp_id_list:
                    
                    print"Employee_id",emp_idd
                    fdate = datetime.datetime.strptime(date_item,'%Y%m%d')
                    day = fdate.weekday()
                    attendance_date =datetime.datetime.strptime(date_item,'%Y%m%d').strftime('%Y-%m-%d')
                    emp_rec_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp_idd),('attendance_date', '=', date_item)]) 
                    for f in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_rec_ids):
                        print"First record in hr employee attendance ",f
                        if(f.employee_id.department_id):
                            print"departmetn found"
                            emp_rec_ids = self.pool.get('hr.schedule').search(cr,uid,[('department_id','=',f.employee_id.department_id.id),('state','=','validate')]) 
                            for sche in self.pool.get('hr.schedule').browse(cr,uid, emp_rec_ids):
                                print "schedule found"
                                if( sche.public_holiday_ids):
                                    print"public holyday found"
                                    for puh in sche.public_holiday_ids:
                                        print"under the public holiday "
                                        print"compare",puh.holiday_date,attendance_date
                                        if(puh.holiday_date == attendance_date):
                                            print"public hol matched"
                                            hr_holiday_rec =True
                                    print"after public holiday"
                   
                    print"the end"
#                     hr_holiday_rec = self.pool.get('hr.public.holiday').search(cr, uid, [('holiday_date','=', attendance_date)])
                    print"before the if conditon"
                    if ( hr_holiday_rec):
                        final_status='public_holiday'

                    else:    
                        if(day==5or day==6):
                            final_status='Holiday'
                        else:    
                            final_status='Absent'

#                     print'--- record not found','for Date --- Before-----',date_item, emp_rec_ids
                    if not emp_rec_ids:
                            self.pool.get('hr.employee.attendance').create(cr, uid, {
                                                'employee_id': emp_idd,
                                                'attendance_date':date_item,
                                                'sign_in': '00:00:00',
                                                'sign_out':'00:00:00',
                                                'attendance_month': str(datetime.datetime.strptime(date_item,'%Y%m%d').strftime('%B')),
                                                'final_status': final_status})

       
#         print '---------- Employees ---------', emp_id_list,'--- Dates',dates
        #wrte method code here
        return True
    def summaries_employee_attendance(self, cr, uid, ids, data):
        
        print"Compute attendance holidays method is called"
        #this place was giving error when i called it on abve method of pulling attendance, it should be rectified, for the time i am giving static dates

        month_comp_date ='2018-03-01'

        if not month_comp_date:
            raise osv.except_osv((),'Date is required')
        year = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%Y'))
        mont = int(datetime.strptime(str(month_comp_date), '%Y-%m-%d').strftime('%m'))
        if(mont <10):
            month ='0'+str(mont)
        else:
            month =''+str(mont) 
        calc_month = str(month) +'-'+str(year) 
        mon_days = calendar.monthrange(year,mont)[1]
        date_from =str(str(year)+'-'+str(month)+'-01')
        date_to =str(str(year)+'-'+str(month)+'-'+str(mon_days))
        emp_ids = self.pool.get('hr.employee').search(cr,uid,[])
       
        if emp_ids: 
            for emp in emp_ids:
                twenty_minutes_late=0
                thirty_minutes_late=0
                absent_this_month = 0
                half_days = 0

                struct_id = 0
                aprove_leave=0

                emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp),('attendance_date','>=',date_from),('attendance_date','<=',date_to)]) 
                for f in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                    #@ubaid, why the following few lines code are removed and f.fucntion? and you are inseting it at the time of pulling
                    #if we follow this way, then we have to pull again again if we want to re-calcualte attendance
                    # ihave also added half day to this code, but we will remove this code from here and move it fields .function

                    print"testing"
#                     if(f.total_short_minutes >=20 and  f.total_short_minutes< 30) and f.final_status !='Status Not Clear':
#                         twenty_minutes_late=twenty_minutes_late+1
#                     if(f.total_short_minutes >= 30 and f.final_status !='Status Not Clear'):
#                         thirty_minutes_late=thirty_minutes_late+1
                    if(f.final_status == 'Absent'):
                        absent_this_month=absent_this_month+1  
#                     if(f.final_status == 'Status Not Clear'):
#                         half_days=half_days+1    
                contr_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',emp)])
                if contr_ids:
                    exists = self.pool.get('hr.monthly.attendance.calculation').search(cr,uid,[('employee_id','=',emp),('name','=',calc_month),('contract_id','=',contr_ids[0])]) 
                      
                    if not exists:
                        self.pool.get('hr.monthly.attendance.calculation').create(cr,uid,{'employee_id':emp,'contract_id':contr_ids[0],'calendar_month':month_comp_date,'name':calc_month,'absentees_this_month':absent_this_month})

                        print "creating new record in attendance calculation table for "+str(emp)
        return
sms_pull_hr_machine_data()










































# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: