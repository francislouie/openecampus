import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
from datetime import date
import time
import datetime

from openerp.report import report_sxw

class sms_report_class_datesheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_class_datesheet, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'print_form': self.print_form,
            'company_name': self.company_name,
            'get_logo': self.get_logo,
            'company_address': self.company_address,
        })
        self.base_amount = 0.00
    
    def company_name(self, data):  
        company = self.pool.get('smsfee.classes.fees').get_company(self.cr, self.uid,self.uid)
        return company
    
    def company_address(self, data):  
        company = self.pool.get('smsfee.classes.fees').get_company(self.cr, self.uid,self.uid)
        street = company.rml_header2
        print "address:",street
        return street
    
    def get_logo(self, data):  
        cpm_id = self.pool.get('res.users').browse(self.cr,self.uid,self.uid).company_id.id
        logo = self.pool.get('res.company').browse(self.cr,self.uid,self.uid).logo_web
        print "logo:",logo
        return logo
    
    def print_form(self):
        result = []
        print "*********************"
        return result 
    
    
report_sxw.report_sxw('report.sms.report.class.datesheet', 
                      'sms.exam.offered', 
                      'addons/sms/report/rml_report_class_datesheet.rml',
                      parser = sms_report_class_datesheet, 
                      header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

