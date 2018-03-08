from openerp.osv import fields, osv
import datetime
import xlwt
import locale
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
              'month': fields.date('Month to Get Absentees')}
            
      
    def pull_attendance_device_data(self, cr, uid, ids, data):

        emp_id = []
        dates = []
        times = []
        item = 0
        item2 = 0
                           
                        item += 1
                         
                     
#                 sqlQ ="""DELETE FROM hr_employee_attendance"""
#                 cr.execute(sqlQ)
                  
                while item2 < len(emp_id):
                    employee_id = self.pool.get('hr.employee').search(cr,uid,[('empleado_account_id','=',str(emp_id[item2]))])
                    employee_rec = self.pool.get('hr.employee').browse(cr,uid,employee_id) 
#                     print '-------------HR Employeee Table-------------'
                    for date in dates:
#                             print "employee empleado id",str(emp_id[item2])
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
                                if date:
                                    if employee_rec:
#                                         print'------------- Employee Id -------------- ', employee_rec[0]['id'], str(datetime.strptime(date,'%Y%m%d').strftime('%B')), emptime_list[0], emptime_list[-1]
                                          
                                        self.pool.get('hr.employee.attendance').create(cr, uid, {
                                            'employee_id': employee_rec[0].id,
                                            'attendance_date': date, 
                                            'sign_in': emptime_list[0],
                                            'sign_out': emptime_list[-1],
                                            'attendance_month': str(datetime.strptime(date,'%Y%m%d').strftime('%B'))})
                                    else:
                                        print " not found on ERP for emplead acc",employee_rec
      
                    item2 += 1
                status = read['status']
        return True    
    
    def compute_attendance_absentees(self, cr, uid, ids, data):
        import datetime, calendar
        
        emp_id_list = []
#         date_item = 0
        dates = []
        
        sqlr ="""SELECT * FROM hr_employee"""
        cr.execute(sqlr)
        rec_ids = cr.fetchall() 
        for record in rec_ids:
            emp_id_list.append(record[0])
            
        d = datetime.date.today()
        year =  d.year
        month = d.month
        num_days = calendar.monthrange(year, month)[1]
        days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        
        for day in days:
            date_stamp = day.strftime('%Y%m%d')
            dates.append(date_stamp)
            
        for date_item in dates:
            for emp_idd in emp_id_list:
                emp_rec_ids = self.pool.get('hr.employee.attendance').search(cr,uid,[('employee_id','=',emp_idd),('attendance_date', '=', date_item)]) 
                print'--- record not found','for Date --- Before-----',date_item, emp_rec_ids
                if not emp_rec_ids:
                        print'--- record not found','for Date ---After -----',date_item, emp_rec_ids
                        self.pool.get('hr.employee.attendance').create(cr, uid, {
                                            'employee_id': emp_idd,
                                            'attendance_date': date_item, 
                                            'sign_in': 0,
                                            'sign_out': 0,
                                            'attendance_month': str(datetime.datetime.strptime(date_item,'%Y%m%d').strftime('%B')),
                                            'final_status': 'Absent'})

       
        print '---------- Employees ---------', emp_id_list,'--- Dates',dates
        #wrte method code here
        return True
        
        
    
sms_pull_hr_machine_data()












































# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: