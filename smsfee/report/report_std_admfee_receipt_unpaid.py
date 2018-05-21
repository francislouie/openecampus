import time
import mx.DateTime
from datetime import datetime
from openerp.report import report_sxw
from openerp import netsvc
import locale
from compiler.ast import Print
from openerp.osv import osv, fields
import xlwt
import socket
from openerp.tools import amount_to_text_en
import babel
 
logger = netsvc.Logger()
result_acc=[]
     
"""This is the main parsor that prints challans for academics and transport with 1 student per page 
   class wise, other parsers that prints class wise challans, should be rmeoved """

class report_std_admfee_receipt_unpaid(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):

        super(report_std_admfee_receipt_unpaid, self).__init__(cr, uid, name, context)
        self.result_temp=[]
        self.localcontext.update( {
            'get_today':self.get_today,
            'get_challans':self.get_challans,
            'get_user_name':self.get_user_name,
            'get_vertical_lines': self.get_vertical_lines,
            'get_due_date':self.get_due_date,
            'get_class_group':self.get_class_group,
            'get_challan_logo':self.get_challan_logo,
            'get_challan_header_lineone':self.get_challan_header_lineone,
            'get_challan_header_linetwo':self.get_challan_header_linetwo,
            'get_challan_header_linethree':self.get_challan_header_linethree,
            'get_challan_footer_one':self.get_challan_footer_one,
            'get_department_logo':self.get_department_logo,
         })
        self.context = context

    def get_challan_logo(self):
        #this will return instute logo on challan
        #another same method will return transport or academics logo, will be added soon
        logo = 'No Logo'
        company_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(company_id)>1:
            return ''
        elif len(company_id) == 1:
            company_recs = self.pool.get('res.company').browse(self.cr, self.uid, company_id)[0]
            logo = company_recs.logo
        return logo

    def get_department_logo(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        if self.datas['form']['category']== 'Academics':
            logo = None
        elif self.datas['form']['category'] == 'Transport':
            logo = company_recs[0].company_clogo_trans
        return logo

    def get_challan_header_lineone(self):
        if self.datas['form']['category'] == 'Academics':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldone from sms_academics_session where
                                    id = (
                                    select acad_session_id from sms_academiccalendar where id=(
                                    select current_class from sms_student where id=""" + str(self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line1 = self.cr.fetchone()[0]
            else:
                print 'class challans works',self.datas['form']['class_id'][0]
                query1 = """select company_cfieldone from sms_academics_session where id = (select acad_session_id from sms_academiccalendar where id=""" + str(
                    self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query1)
                line1 = self.cr.fetchone()[0]
        elif self.datas['form']['category'] == 'Transport':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldone_trans from sms_academics_session where id = (select acad_session_id from sms_academiccalendar where id=( select current_class from sms_student where id=""" + str(self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line1 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldone_trans from sms_academics_session where id = (select acad_session_id from sms_academiccalendar where id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line1 = self.cr.fetchone()[0]
        return line1

    def get_challan_header_linetwo(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------
        if len(rescompany_id)>1:
            return ''
        if self.datas['form']['category']== 'Academics':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldtwo
                    from sms_academics_session where
                   id = (
                                    select acad_session_id from sms_academiccalendar where id=(
                                    select current_class from sms_student where id="""+str(self.datas['form']['student_id'][0])+"""))"""
                self.cr.execute(query)
                line2 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldtwo
                                    from sms_academics_session where
                                   id = ( select acad_session_id from sms_academiccalendar where
                                          id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line2 = self.cr.fetchone()[0]



        elif self.datas['form']['category'] == 'Transport':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldtwo_trans
                               from sms_academics_session where
                              id = (
                                               select acad_session_id from sms_academiccalendar where id=(
                                               select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line2 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldtwo_trans
                                               from sms_academics_session where
                                              id = ( select acad_session_id from sms_academiccalendar where
                                                     id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line2 = self.cr.fetchone()[0]
        return line2
    
    def get_challan_header_linethree(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        # company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        if self.datas['form']['category']== 'Academics':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldthree
                               from sms_academics_session where
                              id = (
                                               select acad_session_id from sms_academiccalendar where id=(
                                               select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line3 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldthree
                                               from sms_academics_session where
                                              id = ( select acad_session_id from sms_academiccalendar where
                                                     id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line3 = self.cr.fetchone()[0]

            # line3 = company_recs[0].company_cfieldthree
        elif self.datas['form']['category'] == 'Transport':
                if 'student_id' in self.datas['form']:
                    query = """select company_cfieldthree_trans
                                   from sms_academics_session where
                                  id = (
                                                   select acad_session_id from sms_academiccalendar where id=(
                                                   select current_class from sms_student where id=""" + str(
                        self.datas['form']['student_id'][0]) + """))"""
                    self.cr.execute(query)
                    line3 = self.cr.fetchone()[0]
                else:
                    query = """select company_cfieldthree_trans
                                                   from sms_academics_session where
                                                  id = ( select acad_session_id from sms_academiccalendar where
                                                         id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                    self.cr.execute(query)
                    line3 = self.cr.fetchone()[0]

            # line3 = company_recs[0].company_cfieldthree_trans
        return line3

    def get_challan_footer_one(self):
        bank_info = self.datas['form']['bank_info']
        return bank_info
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 

    def get_due_date(self):
        due_date = self.datas['form']['due_date']
        due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return due_date 

    def get_class_group(self, data):
        if 'student_id' in self.datas['form']:
            cls_id = self.pool.get('sms.student').browse(self.cr,self.uid,self.datas['form']['student_id'][0]).current_class.id
        else:
            cls_id = self.datas['form']['class_id'][0]
        class_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, cls_id)
        return class_obj.group_id.name  

    def get_challans(self, data):
        challan_list = []
        tlt_amount = 0
        fee_res = []
        
        print"This is first print challan at the time od"
        info_list = []
        challan_dict = {'challan_number':'','candidate_info':'','on_accounts':'','vertical_lines':'','total_amount':'',
                            'amount_in_words':'','amount_after_due_date':'','dbid':'','grand_total':'','grand_lable':'','partial_lable':'' ,'Table_1':''
                            ,'vechil_no':'','vechil_name':''}
        info_dict = {'name':'','father_name':'','class':'','fee_month':'','reg_no':''}
       
        rec = self.pool.get('student.admission.register').browse(self.cr,self.uid,data['active_ids'] )
        print"student admission register",rec.fee_ids
        
        info_dict['reg_no'] = str(rec.registration_no)+' '+'(Admission)'
        info_dict['name'] = rec.name 
        info_dict['father_name'] = rec.father_name
        info_dict['class'] = rec.student_class.name
        fee_month = self.datas['form']['due_date']
        due_date = datetime.strptime(fee_month, '%Y-%m-%d')
        str_date = due_date.strftime('%b %Y')
        info_dict['fee_month'] = str_date
        info_list.append(info_dict)
        print"lenth of the recfee",len(rec.fee_ids)
        if len(rec.fee_ids)>10:
            title = ''
            whole_amount = 0
            for fee in rec.fee_ids :
                fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
                title += fee_name +':'+str(fee.amount)+'\n'
                tlt_amount = tlt_amount+fee.amount
            dict = {'head_name':title,'head_amount':fee.amount}
            fee_res.append(dict)
           
        else:
            for fee in rec.fee_ids :
                fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
                dict = {'head_name':fee_name,'head_amount':fee.amount}
                fee_res.append(dict)
                tlt_amount = tlt_amount+fee.amount
    
#         for fee in rec.fee_ids  :
#             fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
#             dict = {'head_name':fee_name,'head_amount':fee.amount}
#             fee_res.append(dict)
#             tlt_amount = tlt_amount+fee.amount
        challan_dict['challan_number'] =rec.id
        challan_dict['candidate_info'] =  info_list
        challan_dict['on_accounts'] = fee_res
        challan_dict['total_amount'] = tlt_amount
        #*******************convert the amount in text form****************************
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(tlt_amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        #*******************************************************************************
        challan_dict['amount_in_words'] = return_value
        challan_list.append(challan_dict)
        return challan_list                       
     
    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return   user_name



    def get_vertical_lines(self, data):
        line_dots = []
        for num in range(1,30):
            dict = {'line-style':'|'}
            line_dots.append(dict)
        return line_dots
     

     

report_sxw.report_sxw('report.smsfee_std_admfee_receipt_unpaid', 'student.admission.register', 'addons/smsfee/report_std_admfee_receipt_unpaid.rml',parser = report_std_admfee_receipt_unpaid, header=None)
