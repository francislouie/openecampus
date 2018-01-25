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
              'search_filter_salary_str': fields.many2many('hr.payroll.structure','sms_hr_payslips_reports', 'thisobj_id', 'payroll_str_id','Print For'),
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
        
        header_top =  xlwt.Style.easyxf('font: bold 0, color white,  height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour gray80;'
                             )
                 
        
        header_months = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_green;'
                             )
         
        student_white_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white;'
                             )
        student_allowances_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25 ;'
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
        _col = (sheet1.col(1)).width = 200 * 20
        _col = (sheet1.col(2)).width = 300 * 15
        _col = (sheet1.row(3)).height = 200 * 15
        _col = (sheet1.row(3)).height = 200 * 15
        
        #loop via classes, for each class there will be 1 sheet
        sql = """SELECT id,name,number,date_from,date_to from hr_payslip  """ 
        cr.execute(sql)
        slips = cr.fetchall()
        collected_slips = []
        row = 2
        for slip in slips:
            sql2 = """select name,amount from hr_payslip_line where slip_id """+str(slip[0])
            cr.execute(sql2)
            sliplines = cr.fetchall()
            #inner for loop for slip lines here
            #
            
            sheet1.write(row,2, slip[1],student_allowances_rows)
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