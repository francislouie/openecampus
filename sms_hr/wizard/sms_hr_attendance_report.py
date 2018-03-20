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
              'employee_id': fields.many2one('hr.employee', 'Employee'),
              'options' :fields.selection([('val1', 'Print for single department'), ('val2', 'Print for all active employees'),('val3', 'Print for single employee')],'Options',required = True),
            }
    _defaults = {
                
                }
     
    def print_sms_hr_attendance_report(self, cr, uid, ids, data):
        employee_id=0
        department_id=0
        record = self.read(cr, uid, ids)[0]
        print"This is form date",record
        if record['employee_id']:
            employee_id= record['employee_id'][0]
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
       
        return True
    
sms_hr_attendance_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: