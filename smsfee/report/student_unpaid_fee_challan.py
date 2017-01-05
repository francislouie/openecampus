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
     
class unpaid_fee_challan_parser(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
 
        super(unpaid_fee_challan_parser, self).__init__(cr, uid, name, context)
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
        challan_list = []
        stu_rec = self.pool.get('sms.student').browse(self.cr ,self.uid , self.ids[0])
        
        self.pool.get('smsfee.receiptbook').check_fee_challans_issued(self.cr, self.uid ,stu_rec.current_class.id ,stu_rec.id)
        
        challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid,[('student_class_id','=', stu_rec.current_class.id),
                                                                                    ('student_id','=', stu_rec.id),
                                                                                    ('state','=','fee_calculated')])
        if challan_ids:
            rec_challan_ids = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid,challan_ids) 
            for challan in rec_challan_ids:
                challan_dict = {'challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
                challan_dict['challan_number'] =  self.get_challan_number(challan.id)
                challan_dict['candidate_info'] = self.get_candidate_info(challan.student_id.id)
                if self.get_on_accounts(challan.id) == []:
                    print "*************"
                    challan_dict['on_accounts'] =  ' '
                else:
                    challan_dict['on_accounts'] =  self.get_on_accounts(challan.id)
                challan_dict['total_amount'] =  self.get_total_amount(challan.id)
                challan_dict['amount_in_words'] =   self.get_amount_in_words(challan.id)
                challan_list.append(challan_dict)
                
        return challan_list  
     
    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return   user_name
 
    def get_vertical_lines(self, data):
        line_dots = []
        for num in range(1,20):
            dict = {'line-style':'|'}
            line_dots.append(dict)
        return line_dots
     
    def get_vertical_lines_total(self, data):
        line_dots = []
        challan = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data)
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
     
    def get_banks(self):
        banks_ids = self.pool.get('res.company').search(self.cr,self.uid,[])
        banks_recs = self.pool.get('res.company').browse(self.cr,self.uid,banks_ids)
        for rec in banks_recs:
            bank = rec.fee_reception_account_bank.name + rec.fee_reception_account_bank.code 
        return bank
 
    def get_challan_number(self, data):
        line_dots = []
#         
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         challan_str = str(challan.challan_no)
#         return challan_str.split("-")[1] + " (" + challan_str.split("-")[0]+ ")"
        return '__________'
 
    def get_candidate_info(self, data):
        info_list = []
        stdrec = self.pool.get('sms.student').browse(self.cr,self.uid,self.ids[0])
        info_dict = {'name':'','father_name':'','Class':'','semester':''}
         
        info_dict['name'] = stdrec.name
        info_dict['father_name'] = stdrec.father_name
        info_dict['class'] = stdrec.current_class.name
        info_list.append(info_dict)
        print "info_list>>>>>>>>>>>>",info_list
        return info_list
 
    def get_on_accounts(self, data):
        result = []
        challans = []
        lines_ids = self.pool.get('smsfee.receiptbook.lines').search(self.cr,self.uid, [('receipt_book_id','=',data)])
        print "++++++++",  lines_ids   
        if lines_ids:
             challans = self.pool.get('smsfee.receiptbook.lines').browse(self.cr,self.uid,lines_ids)
        counter = 1
        for challan in challans:
             print challan.fee_name,"+++++======+++++++",challan.fee_amount
             if counter <7:
                 dict = {'head_name':challan.fee_name,'head_amount':challan.fee_amount}
                 result.append(dict)
             counter = counter + 1 
        return result
     
    def get_total_amount(self, data):
        line_dots = []
        receipt = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data)
#         total_amount_str = str(babel.numbers.format_currency((receipt.total_amount), "" )) + " /="
        print receipt,"receipt.total_paybles",receipt.total_paybles 
        total_amount_str = receipt.total_paybles
        return total_amount_str
     
    def get_amount_in_words(self,data):
        amount = challan = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data).total_paybles
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        return return_value
     
report_sxw.report_sxw('report.smsfee_stu_unpaidfee_receipt_name', 'smsfee.classfees.register', 'addons/smsfee/student_unpaid_fee_challan_view.rml',parser = unpaid_fee_challan_parser, header=None)
