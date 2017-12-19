from datetime import date
import time
import datetime

from openerp.report import report_sxw

class sms_report_datesheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_datesheet, self).__init__(cr, uid, name, context = context)
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
        _pooler = self.pool.get('sms.exam.offered')
        rec = _pooler.browse(self.cr, self.uid,self.ids[0])
        
        my_dict = {'exam_name':'','class':'','child':'','inner_dict':''}
        inner_dict = {'day':'','date':'','subject':'','invigilator':''}
        
        for datesheet in rec.datesheet_ids:
            res = []
            my_dict = {'exam_name':'','class':'','child':'','inner_dict':''}
            
            print   datesheet.academiccalendar.name,"******",datesheet.name
            find =  datesheet.name.find('(')
            print find
            if find == -1:
                print "_-----------------------------------------------1"
                my_dict['exam_name'] = datesheet.name+' ('+datesheet.academiccalendar.name+')'
                my_dict['class'] =  None
            else:
                print "nooooooooooooooooooooooooooooooooooooooooot11111111111111"
                my_dict['class'] =  None
                my_dict['exam_name'] = datesheet.name
            
            
            for i in datesheet.datesheet_lines:
                
                inner_dict = {'day':'','date':'','subject':'','invigilator':''}
                inner_dict['date'] = i.paper_date
                inner_dict['subject'] =  i.subject.name
                inner_dict['invigilator'] = i.invigilator.name
                
                if i.paper_date:
                    day = datetime.datetime.strptime(i.paper_date, '%Y-%m-%d').strftime('%A')
                    inner_dict['day'] = day
                else:
                    inner_dict['day'] = None
                
                res.append(inner_dict)
                my_dict['inner_dict'] = res
                
            result.append(my_dict)
            
        return result
    
    
report_sxw.report_sxw('report.sms.report.datesheet', 
                      'sms.exam.offered', 
                      'addons/sms/report/rml_report_datesheet_view.rml',
                      parser = sms_report_datesheet, 
                      header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

