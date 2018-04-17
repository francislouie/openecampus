from openerp.osv import fields, osv
import datetime
import re
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

class sms_hr_payslips_reports(osv.osv_memory):
    """
    This wizard create reports for payslips that are generated during a specific duration and that are needed to be singn by concerns person
    2) this wizard will aslo export data to ms excle needed by bank for salary transfer, the format of the file should be according to the statndard
    formate given by the bank.
    """
    
    
    _name = "sms.hr.payslips.reports"
    _description = "Prints defaulter list"
    _columns = {
              'payslip_start_date': fields.date('From',required = True),
              'payslip_end_date': fields.date('To',required = True),
#               'search_filter_salary_str': fields.many2many('hr.payroll.structure','sms_hr_payslips_reports', 'thisobj_id', 'payroll_str_id','Print For'),
              'report_type': fields.selection([('signature_sheet','Signature Sheet'),('bank_sheet','Bank Sheet')],'Options'),
              'order_by':fields.selection([('employee_name','Employee Name'),('payslip_no','Payslip No'),('salry_strucre','Salary Structure'),('designation','Designation')],'Sort By'),
               }
    _defaults = {
                 'order_by':'employee_name',
                 'report_type':'signature_sheet',
           }
    
    def print_payslipslist_signature_list(self, cr, uid, ids, data):
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
        
        
        sheet1=book.add_sheet(str("Slips")+" "+str("--"),cell_overwrite_ok=True)
       # title = this_class.name
        #class_ctr = class_ctr + 1
        _col = (sheet1.col(2)).width = 200 * 20
        _col = (sheet1.col(3)).width = 700 * 20
        _col = (sheet1.col(4)).width = 200 * 20
        _col = (sheet1.col(5)).width = 200 * 20
        _col = (sheet1.col(6)).width = 200 * 20
        _col = (sheet1.col(7)).width = 200 * 20
        _col = (sheet1.col(8)).width = 200 * 20
        _col = (sheet1.col(9)).width = 200 * 20
        _col = (sheet1.col(10)).width = 200 * 20
        _col = (sheet1.col(11)).width = 200 * 20
        _col = (sheet1.col(12)).width = 200 * 20
#         _col = (sheet1.col(2)).width = 300 * 15
        _col = (sheet1.row(0)).height = 100 * 15
        _col = (sheet1.row(1)).height = 60 * 15
        
#         _col = (sheet1.row(3)).height = 200 * 15
        
        #loop via classes, for each class there will be 1 sheet
        sql = """SELECT id,name,number,date_from,date_to from hr_payslip  """ 
        cr.execute(sql)
        slips = cr.fetchall()
        collected_slips = []
        row = 0
        str_month = re.sub('-', '', slips[0][3])
        slip_month = datetime.strptime(str_month,'%Y%m%d').strftime('%B-%Y')
        print"------ Slip Month  ------------", slip_month
       
        sheet1.write_merge(row, row, 2, 12, 'Salary Slip List for '+ slip_month, header_top)
        sheet1.write(row+1, 2, 'Slip No', header_months) 
        sheet1.write(row+1, 3, 'Employee', header_months) 
        sheet1.write(row+1, 4, 'Salary Structure', header_months) 
        sheet1.write(row+1, 5, 'HRA', header_months) 
        sheet1.write(row+1, 6, 'MDA', header_months) 
        sheet1.write(row+1, 7, 'Conv. Allowance', header_months) 
        sheet1.write(row+1, 8, 'GROSS', header_months) 
        sheet1.write(row+1, 9, 'Attendance Deduct', header_months) 
        sheet1.write(row+1, 10, 'Sec. Deduct', header_months) 
        sheet1.write(row+1, 11, 'Base Salary', header_months) 
        sheet1.write(row+1, 12, 'Net Salary', header_months) 
    
        
        row = 2
        for slip in slips:
            sql2 = """select name,amount,code,total from hr_payslip_line where slip_id="""+str(slip[0])+""""""
            
            cr.execute(sql2)
            sliplines = cr.fetchall()
            print'--------- Slip Lines ----------', sliplines
            #inner for loop for slip lines here
            for sline in sliplines:
                print'-------- Sline --------', sline
                sheet1.write(row, 2, slip[0], student_allowances_rows) 
                sheet1.write(row, 3, slip[1], student_allowances_rows)
                if 'HRA' in sline:
                    sheet1.write(row, 5, sline[3], student_allowances_rows)
                if 'MDA' in sline:
                     sheet1.write(row, 6, sline[3], student_allowances_rows)
                if 'CNA' in sline:
                     sheet1.write(row, 7, sline[3], student_allowances_rows)
                if 'GROSS' in sline:
                     sheet1.write(row, 8, sline[3], student_allowances_rows)
                if 'ATD' in sline:
                     sheet1.write(row, 9, sline[3], student_allowances_rows)  
                if 'SDE' in sline:
                     sheet1.write(row, 10, sline[3], student_allowances_rows) 
                if 'BASE' in sline:
                     sheet1.write(row, 11, sline[3], student_allowances_rows)  
                if 'NET' in sline:
                     sheet1.write(row, 12, sline[3], student_allowances_rows)   
                          
                sheet1.write(row, 4, sline[0], student_allowances_rows)
#                 sheet1.write(row, 6, sline[1], student_allowances_rows)
            row = row + 1        
        path = os.path.join(os.path.expanduser('~'),'slips.xls')
        book.save(path)
        return
    
    
    def print_payslipslist_bank_sheet(self, cr, uid, ids, data):
        result = []
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'hr.payslip',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee_defaulter_studnent_list_name',
            'datas': datas,
        }
    
                
sms_hr_payslips_reports()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: