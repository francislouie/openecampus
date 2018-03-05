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
                            search_rec1 = self.pool.get('hr.attendance').search(cr,uid,[('empleado_account_id','=',str(emp_id[item2])),('attendance_date', '=', str(date))])                                            
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
        
        #wrte method code here
        return 
        
    
sms_pull_hr_machine_data()












































# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: