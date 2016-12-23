import pooler
import time
import mx.DateTime
import datetime
from report import report_sxw
import netsvc
import locale
from compiler.ast import Print
from osv import osv, fields
import xlwt
import socket
from tools import amount_to_text_en
import babel
 
logger = netsvc.Logger()
result_acc=[]
     
class transport_unpaid_fee_challans(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
 
        super(transport_unpaid_fee_challans, self).__init__(cr, uid, name, context)
        self.result_temp=[]
        self.localcontext.update( {
            'get_today':self.get_today,
            'get_challans':self.get_challans,
            'get_user_name':self.get_user_name,
            'get_vertical_lines': self.get_vertical_lines,
            'get_vertical_lines_total': self.get_vertical_lines_total,
            'get_banks':self.get_banks,
            'get_challan_number':self.get_challan_number,
            'get_candidate_info':self.get_candidate_info,
            'get_on_accounts':self.get_on_accounts,
            'get_total_amount':self.get_total_amount,
            'get_amount_in_words':self.get_amount_in_words,
         })
        self.context = context
     
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 
     
    def get_challans(self, data):
        
        #********************************************************************************************
#         this_form = self.datas['form']
#         cls_id = self.datas['form']['class_id'][0]
#         challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid,[('student_class_id','=',cls_id),('state','=','fee_calculated')]) 
#         if challan_ids:
#             
#             rec_challan_ids = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid,challan_ids) 
#             for challan in rec_challan_ids:
#                 challan_dict = {'banks':'','challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
#                 challan_dict['banks'] = self.get_banks(challan.id)
#                 challan_dict['challan_number'] = self.get_challan_number(challan.id)
#                 challan_dict['candidate_info'] = self.get_candidate_info(challan.student_id.id)
#                 challan_dict['on_accounts'] = self.get_on_accounts(challan.id)
#                 challan_dict['total_amount'] = self.get_total_amount(challan.id)
#                 challan_dict['amount_in_words'] = self.get_amount_in_words(challan.id)
#                 challan_list.append(challan_dict)
#             print "get challan===================",challan_list
        
        #********************************************************************************************
        
        challan_list = []
        print "------------++++++++++++++++++++++++++--------------------"
        ###########print challan at the time of admission for paying fee (it is before admitting student)
        if data['model'] == 'student.admission.register':
            tlt_amount = 0
            rec = self.pool.get('student.admission.register').browse(self.cr,self.uid,data['active_ids'])
            info_dict = {'name':rec.name,'father_name':rec.father_name,'Class':rec.student_class.name,'semester':''}
            
            fee_res = []
            challan_dict = {'banks':'','challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
            for fee in rec.fee_ids  :
                fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
                dict = {'head_name':fee_name,'head_amount':fee.amount}
                fee_res.append(dict)
                tlt_amount = tlt_amount+fee.amount
                
            challan_dict['banks'] = '--'
            challan_dict['challan_number'] = rec.registration_no
            challan_dict['candidate_info'] =  [info_dict]
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
        else:
            this_form = self.datas['form']
            cls_id = self.datas['form']['class_id'][0]
            challan_ids = self.pool.get('sms.transportfee.challan.book').search(self.cr, self.uid,[('student_class_id','=',cls_id),('state','=','fee_calculated')])
            if challan_ids:
                rec_challan_ids = self.pool.get('sms.transportfee.challan.book').browse(self.cr, self.uid,challan_ids) 
                for challan in rec_challan_ids:
                    challan_dict = {'banks':'','challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
                    challan_dict['banks'] = self.get_banks(challan.id)
                    challan_dict['challan_number'] = self.get_challan_number(challan.id)
                    challan_dict['candidate_info'] = self.get_candidate_info(challan.student_id.id)
                    challan_dict['on_accounts'] = self.get_on_accounts(challan.id)
                    challan_dict['total_amount'] = self.get_total_amount(challan.id)
                    challan_dict['amount_in_words'] = self.get_amount_in_words(challan.id)
                    challan_list.append(challan_dict)
                print "get challan===================",challan_list
                
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
     
    def get_vertical_lines_total(self, data):
        line_dots = []
        challan = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data)
#         start = len(challan.receiptbook_lines_ids)
        start = 5
        if start >=14:
            dict = {'line-style':'|'}
            line_dots.append(dict)
        else:
            for num in range(start,14):
                dict = {'line-style':'|'}
                line_dots.append(dict)
        return line_dots    
     
    def get_banks(self, data):
        print "get banks",data
#         banks = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         for category in challan.challan_banks:
#             dict = {'bank_name':category.name.name}
#             banks.append(dict) 
#         return banks
        return '--'
 
    def get_challan_number(self, data):
        line_dots = []
#         
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         challan_str = str(challan.challan_no)
#         return challan_str.split("-")[1] + " (" + challan_str.split("-")[0]+ ")"
        return '__________'
 
    def get_candidate_info(self, data):
        info_list = []
        #print "data",data
        #print "self",self
        stdrec = self.pool.get('sms.student').browse(self.cr,self.uid,data)
        info_dict = {'name':'','father_name':'','Class':'','semester':''}
         
        info_dict['name'] = stdrec.name
        info_dict['father_name'] = stdrec.father_name
        info_dict['class'] = stdrec.current_class.name
        info_list.append(info_dict)
        #print "info_list>>>>>>>>>>>>",info_list
        return info_list
 
    def get_on_accounts(self, data):
        result = []
        lines_ids = self.pool.get('sms.transport.fee.challan.lines').search(self.cr,self.uid, [('receipt_book_id','=',data)])
        #print "++++++++",     
        if lines_ids:
             challans = self.pool.get('sms.transport.fee.challan.lines').browse(self.cr,self.uid,lines_ids)
        for challan in challans:
             dict = {'head_name':'Transport Fee','head_amount':challan.fee_amount}
             result.append(dict) 
        return result
     
    def get_total_amount(self, data):
        line_dots = []
        receipt = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data)
#         total_amount_str = str(babel.numbers.format_currency((receipt.total_amount), "" )) + " /="
        #print receipt,"receipt.total_paybles",receipt.total_paybles 
        total_amount_str = receipt.total_payables
        return total_amount_str
     
    def get_amount_in_words(self,data):
        amount = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data).total_payables
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        return return_value
     
report_sxw.report_sxw('report.smstransport_unpaid_receipts_name', 'sms.transport.fee.payments', 'addons/smstransport/smstransport_unpaid_receipts_report.rml',parser = transport_unpaid_fee_challans, header=None)
