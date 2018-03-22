from openerp.osv import fields, osv
import datetime
import re
import xlwt
import locale
from datetime import datetime
from reportlab.pdfgen import canvas
import sys
import subprocess
import time
import urllib
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from xml.etree import ElementTree
import os
from numpy import require

class sms_hr_attendance_report(osv.osv_memory):
    """
    This wizard is use to print attendance .
    """
    
    
    _name = "sms.hr.attendance.report"
    _description = "sms hr attendance report"
    _columns = {
              'start_date': fields.date('From',required = True),
              'end_date': fields.date('To',required = True),
              'department_id': fields.many2one('hr.department', 'Department'),
              'employee_id': fields.many2many('hr.employee','hr_employee_sms_hr_attendance_rel','hr_employee','sms_hr_att', 'Employee'),
              'options' :fields.selection([('1', 'Print for single department'), ('2', 'Print for all active employees'),('3', 'Print for selected employees')],'Options',required = True),
            }
    _defaults = {
                
                }
     
    def print_sms_hr_attendance_report(self, cr, uid, ids, data):
        employee_id = 0
        department_id = 0
        record = self.read(cr, uid, ids)[0]
        print"This is form date",record
        if record['employee_id']:
            employee_id= record['employee_id']
        if record['department_id']:    
            department_id= record['department_id'][0]
        start_date= record['start_date']   
        end_date= record['end_date'] 
        options= record['options'] 
        print"Employee id",employee_id
        print"department id",department_id
        print"start_date ",start_date
        print"end_date ",end_date
        print"options ",options
        
        
        
        result = []
        print "slipssssssssssssssssssssssssssssssssssssssssssssssssssssss method called"
        book=xlwt.Workbook()
        
        header_top =  xlwt.Style.easyxf('font: bold on, color white,  height 450;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour light_blue;'
                             )
                 
        
        header_months = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25;'
                             )
         
        student_white_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white;'
                             )
        student_allowances_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white ;'
                             )
        
        student_deductions_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25 ;'
                             )
        student_netsalary_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25 ;'
                             )
        
        student_gross_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25 ;'
                             )
        
        

        
        if options == '3':
            for employee in employee_id:
                sql0 = """SELECT name_related from hr_employee where id = """ +  str(employee) 
                cr.execute(sql0)
                emp_name = cr.fetchone()[0]
                print'-------- Employee Name ---------', emp_name
                sql = """SELECT attendance_date,sign_in,sign_out from hr_employee_attendance where employee_id = """ +  str(employee) + """ and attendance_date >= '""" + str(start_date) + """' and attendance_date <= '""" + str(end_date) + """'"""
#                 select attendance_date,sign_in,sign_out from hr_employee_attendance where employee_id = 8 and attendance_date >='2018-03-01' and attendance_date <='2018-03-31'
                cr.execute(sql)
                emp_dates = cr.fetchall()
                
                sheet1=book.add_sheet(str(emp_name),cell_overwrite_ok=True)
    
                _col = (sheet1.col(2)).width = 400 * 20
                _col = (sheet1.col(3)).width = 400 * 20
                _col = (sheet1.col(4)).width = 400 * 20
                _col = (sheet1.col(5)).width = 200 * 20
                _col = (sheet1.col(6)).width = 200 * 20
                _col = (sheet1.col(7)).width = 200 * 20
                _col = (sheet1.col(8)).width = 200 * 20
                _col = (sheet1.col(9)).width = 200 * 20
                _col = (sheet1.col(10)).width = 200 * 20
                _col = (sheet1.col(11)).width = 200 * 20
                _col = (sheet1.col(12)).width = 200 * 20
                _col = (sheet1.row(0)).height = 100 * 15
                _col = (sheet1.row(1)).height = 60 * 15
                
                row = 0
                sheet1.write_merge(row, row, 2, 4, 'Attendance Details for '+ emp_name + ' from ' + start_date + ' to '+end_date, header_top)
                sheet1.write(row+1, 2, 'Attendance Date', header_months) 
                sheet1.write(row+1, 3, 'Sign In Time', header_months) 
                sheet1.write(row+1, 4, 'Sing Out Time', header_months) 
                row = 2
                for sline in emp_dates:
                    print'-------- Sline --------', sline
                    sheet1.write(row, 2, sline[0], student_allowances_rows)    
                    sheet1.write(row, 3, sline[1], student_allowances_rows)  
                    sheet1.write(row, 4, sline[2], student_allowances_rows)  
                    row = row + 1  
                
            path = os.path.join(os.path.expanduser('~'),'attendance_report.xls')
            book.save(path)
        return True
    
sms_hr_attendance_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: