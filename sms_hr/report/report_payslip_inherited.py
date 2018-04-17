#-*- coding:utf-8 -*-

##############################################################################
#this parser actually replaced actaull payslip parser of module hr_payroll
##############################################################################
import os
import xlwt
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class report_payslip_inherited(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_payslip_inherited, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines': self.get_payslip_lines,
            'print_payslipslist_signature_list': self.print_payslipslist_signature_list
        })

    def get_payslip_lines(self, obj):
        print "inherited report called lled lled called"
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                ids.append(obj[id].id)
                
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
            print "Test Values for Payslips ----   ", res
        return res
    
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

report_sxw.report_sxw('report.payslip_inherited', 'hr.payslip', 'sms_hr/report/report_payslip_inherited.rml', parser=report_payslip_inherited)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
