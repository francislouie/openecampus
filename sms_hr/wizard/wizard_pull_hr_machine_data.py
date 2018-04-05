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
    """
    
    """
    
    _name = "sms.pull.hr.machine.data"
    _description = "Pull Datat"
    _columns = {
              'pull_for_device': fields.selection([('all','Pull For All Device')],'Device'),
              'month': fields.date('Month to Get Absentees'),
              'month_comp': fields.date('Month For computing absentees'),
              'fetch_all_records': fields.boolean('Get All Previous Records')
              }
            
      
    def pull_attendance_device_data(self, cr, uid, ids, data):
        import requests
        
        # Check if Month is selected in the wizard
        month_comp_date = self.read(cr, uid, ids)[0]['month_comp']
        if not month_comp_date:
            raise osv.except_osv((),'Date is required')
        
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
 
                     
        while status == 'ok':
            item = 0
            # Development API
#             r = requests.get('http://api.smilesn.com/empleado/test_attendance.php?org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id=24')
            # Production API
            r = requests.get('http://api.smilesn.com/attendance_pull.php?operation=pull_attendance&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id='+str(branch_id))
            if(r.status_code == 200):
#                 sqlQ ="""DELETE FROM hr_attendance"""
#                 cr.execute(sqlQ)
                read = r.json()
                print'----------- RAW DATA ------------------',read
                if(read['status']=='ok'):
                    ack_id = read['acknowledge_id']
                    ack = requests.get('http://api.smilesn.com/attendance_pull.php?operation=acknowledge&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id='+str(branch_id)+'&ack_id='+str(ack_id)) 
#                     print "---------------------------     json response    -----------------------------",read,ack
                    for att_record in read['att_records']:
#                         print "empleado id",att_record['user_empleado_id']
                        if att_record['user_empleado_id'] not in emp_id:
                            emp_id.append(att_record['user_empleado_id'])
                                
                    for att_record in read['att_records']:
                        att_value = att_record['att_time']
                        att_date = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                        if att_date not in dates:
                            dates.append(att_date)
                        
                    for att_record in read['att_records']:
                        att_value = att_record['att_time']
                        att_time = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H%M%S')
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
                                                
                                    date_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                                    time_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H:%M:%S')
                                    for date in dates:
                                        if date_stamp == date:
                                            search_rec = self.pool.get('hr.attendance').search(cr,uid,[('attendance_date','=',date_stamp),('attendance_time','=',time_stamp)])   
                                            if not search_rec:
                                                result = self.pool.get('hr.attendance').create(cr, uid, {
                                                'attendance_date': date_stamp,
                                                'attendance_time': time_stamp,                            
                                                'status': 'Sign In',
                                                'action':'sign_in',
                                                'name':'2018-01-29 07:25:00',
                                                'empleado_account_id': user_id, 
                                                'emp_regno_on_device': biometric_id,
                                                'employee_name': employee_rec[0].name_related
                                                })  
#                                                   
                        item += 1
  
            status = read['status']
          
                                   
                         
#         sqlQ ="""DELETE FROM hr_employee_attendance"""
#         cr.execute(sqlQ)
#         print'--------- All Dates ----------------------- ' , dates 
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
<<<<<<< HEAD
#         self.compute_attendance_holidays(cr, uid, ids, data)
=======
        self.compute_attendance_holidays(cr, uid, ids, data)
>>>>>>> 8bfc226cc0b30b777d6fd78c30e696e8d30b60b6
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
                for emp_idd in emp_id_list:
                    emp_rec_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp_idd),('attendance_date', '=', date_item)]) 
                    fdate = datetime.datetime.strptime(date_item,'%Y%m%d')
                    day = fdate.weekday()

                    print" date ",date_item
                    attendance_date =datetime.datetime.strptime(date_item,'%Y%m%d').strftime('%Y-%m-%d')
                    hr_holiday_rec = self.pool.get('hr.public.holiday').search(cr, uid, [('holiday_date','=', attendance_date)])
                    if hr_holiday_rec:
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
    def compute_attendance_holidays(self, cr, uid, ids, data):
        
        print"Compute attendance holidays method is called"
        #this place was giving error when i called it on abve method of pulling attendance, it should be rectified, for the time i am giving static dates
<<<<<<< HEAD
#         month_comp_date ='2018-03-01'
        month_comp_date =data
=======
        month_comp_date ='2018-03-01'
>>>>>>> 8bfc226cc0b30b777d6fd78c30e696e8d30b60b6
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
<<<<<<< HEAD
=======
                struct_id = 0
                aprove_leave=0
>>>>>>> 8bfc226cc0b30b777d6fd78c30e696e8d30b60b6
                emp_att_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp),('attendance_date','>=',date_from),('attendance_date','<=',date_to)]) 
                for f in self.pool.get('hr.employee.attendance').browse(cr,uid, emp_att_ids):
                    #@ubaid, why the following few lines code are removed and f.fucntion? and you are inseting it at the time of pulling
                    #if we follow this way, then we have to pull again again if we want to re-calcualte attendance
                    # ihave also added half day to this code, but we will remove this code from here and move it fields .function
<<<<<<< HEAD
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
=======
                    
                    if(f.total_short_minutes >=20 and  f.total_short_minutes< 30) and f.final_status !='Status Not Clear':
                        twenty_minutes_late=twenty_minutes_late+1
                    if(f.total_short_minutes >= 30 and f.final_status !='Status Not Clear'):
                        thirty_minutes_late=thirty_minutes_late+1
                    if(f.final_status == 'Absent'):
                        absent_this_month=absent_this_month+1  
                    if(f.final_status == 'Status Not Clear'):
                        half_days=half_days+1    
                contr_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',emp)])
                print"Tweenty Late ",twenty_minutes_late
                print"Thirty late ",thirty_minutes_late
                print "employee id",emp
                
                #@ubaid, this is not good code, we should not keep static ids, you can create a fields.function for it that will check employess slary stc and will assgin leaves
                #we will remove this code from here soon
                sql = """SELECT struct_id from  hr_contract where employee_id = """+str(emp)+ """"""
                print"query struct_id",sql
                cr.execute(sql)
                ft_ids = cr.fetchone() 
                if ft_ids:
                    struct_id = ft_ids[0]
                if struct_id == 11:
#                     absent_this_month =  absent_this_month-1
                    aprove_leave=1
>>>>>>> 8bfc226cc0b30b777d6fd78c30e696e8d30b60b6
                if contr_ids:
                    exists = self.pool.get('hr.monthly.attendance.calculation').search(cr,uid,[('employee_id','=',emp),('name','=',calc_month),('contract_id','=',contr_ids[0])]) 
                      
                    if not exists:
<<<<<<< HEAD
                        self.pool.get('hr.monthly.attendance.calculation').create(cr,uid,{'employee_id':emp,'contract_id':contr_ids[0],'calendar_month':month_comp_date,'name':calc_month,'absentees_this_month':absent_this_month})
=======
                        self.pool.get('hr.monthly.attendance.calculation').create(cr,uid,{'employee_id':emp,'contract_id':contr_ids[0],'calendar_month':month_comp_date,'name':calc_month,'twenty_minutes_late':twenty_minutes_late,'thirty_minutes_late':thirty_minutes_late,'half_days':half_days,'absentees_this_month':absent_this_month,'approved_leaves_this_month':aprove_leave})
>>>>>>> 8bfc226cc0b30b777d6fd78c30e696e8d30b60b6
                        print "creating new record in attendance calculation table for "+str(emp)
        return
sms_pull_hr_machine_data()












































# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: