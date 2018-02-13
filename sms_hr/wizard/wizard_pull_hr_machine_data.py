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
               }
        
    def pull_attendance_device_data(self, cr, uid, ids, data):
        result = []
        emp_id = []
        dates = []
        times = []
        item = 0
        item2 = 0
#         import requests
#         r = requests.get('http://api.smilesn.com/attendance_pull.php?operation=pull_attendance&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3')
#         read = r.json()
#         print "json response",read
#         for gg in read['att_records']:
#             print "gg as whole",gg
#             print "att_time",gg['att_time']
#             print "bio_id",gg['bio_id']
#             print "user_empleado_id id",['user_empleado_id']
#             print "device_id id",['device_id']

        import requests
        r = requests.get('http://api.smilesn.com/attendance_pull.php?operation=pull_attendance&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3&branch_id=24')
        if(r.status_code == 200):
            read = r.json()
            
            print "---------------------------     json response    -----------------------------",read
            for att_record in read['att_records']:
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
#                 print "----------    Data of user No   ---------------------",emp_id[item] 
                for att_records in read['att_records']: 
                
                        if att_records['user_empleado_id'] == emp_id[item]:
        
                            att_value = att_records['att_time']           
                            biometric_id = att_records['bio_id']
                            user_id = att_records['user_empleado_id']
                            device_id = att_records['device_id']
                                    
                            date_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%Y%m%d')
                            time_stamp = datetime.strptime(att_value,'%Y%m%d%H%M%S').strftime('%H%M%S')
                            for date in dates:
                                if date_stamp == date:
                                    search_rec = self.pool.get('hr.attendance').search(cr,uid,[('attendance_date','=',date_stamp),('attendance_time','=',time_stamp)])   
                                    if not search_rec:
                                        print "----------  No Records Found for Attendance of this Employee  ----------",search_rec
                                        result = self.pool.get('hr.attendance').create(cr, uid, {
                'attendance_date': date_stamp,
                'attendance_time': time_stamp,                            
                'status': 'Sign In',
                'action':'sign_in',
                'name':'2018-01-29 07:25:00',
                'empleado_account_id': user_id, 
                'emp_regno_on_device': biometric_id,})
                                    else:
                                        print '-------------  Sign Out  ----------------'
                                        recs_found = self.pool.get('hr.attendance').browse(cr,uid,search_rec) 
                                        for rec in recs_found:
                                            if rec['status'] == 'sign_in':
                                                result = self.pool.get('hr.attendance').create(cr, uid, {
                'attendance_date': date_stamp,
                'attendance_time': time_stamp, 
                'status': 'Sign Out',
                'action':'sign_out',
                'name':'2018-01-29 07:25:00',
                'empleado_account_id': user_id, 
                'emp_regno_on_device': biometric_id,})
                                            else:
                                                print '-------------  Sign In  ----------------'
                                                result = self.pool.get('hr.attendance').create(cr, uid, {
                'attendance_date': date_stamp,
                'attendance_time': time_stamp, 
                'status': 'Sign In',
                'action':'sign_in',
                'name':'2018-01-29 07:25:00',
                'empleado_account_id': user_id, 
                'emp_regno_on_device': biometric_id,})
                 
                item += 1
            
            while item2 < len(emp_id):
                search_rec1 = self.pool.get('hr.attendance').search(cr,uid,[('empleado_account_id','=',emp_id[item2])]) 
                if search_rec1:
               
                    recs_found1 = self.pool.get('hr.attendance').browse(cr,uid,search_rec1) 
                    for rec1 in recs_found1:
                        print "Hello  ---------------- Man =----------------------- How",rec1

                        if rec1.attendance_time < 120000:
                            print "Hello  ---------------- sign in=----------------------- How"
                            att_time1 = str(datetime.strptime(rec1.attendance_time,'%H%M%S').strftime('%H:%M:%S'))
                            self.pool.get('hr.attendance').write(cr, uid, rec1.id, {'status': 'Sign In', 'attendance_time': att_time1})
                        else:
                            print "Hello  ---------------- sign out=----------------------- How"
                            att_time1 = str(datetime.strptime(rec1.attendance_time,'%H%M%S').strftime('%H:%M:%S'))
                            self.pool.get('hr.attendance').write(cr, uid, rec1.id, {'status': 'Sign Out', 'attendance_time': att_time1})
                item2 += 1
                
        return True    
sms_pull_hr_machine_data()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: