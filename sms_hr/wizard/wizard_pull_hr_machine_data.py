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
        
        #code from here is removed due to bilal commit, that will be added soon
        
        
        
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