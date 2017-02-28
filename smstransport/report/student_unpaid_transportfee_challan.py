import time
import mx.DateTime
from datetime import datetime
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
     
class unpaidtransport_fee_challan_parser(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
 
        super(unpaidtransport_fee_challan_parser, self).__init__(cr, uid, name, context)
        self.result_temp=[]
        self.localcontext.update({
                        'get_today':self.get_today,
                        'get_challans':self.get_challans,
                        'get_user_name':self.get_user_name,
                        'get_vertical_lines': self.get_vertical_lines,
                        'get_vertical_lines_total': self.get_vertical_lines_total,
                        'get_banks':self.get_banks,
                        'get_banks_2':self.get_banks_2,
                        'get_challan_number':self.get_challan_number,
                        'get_candidate_info':self.get_candidate_info,
                        'get_on_accounts':self.get_on_accounts,
                        'get_total_amount':self.get_total_amount,
                        'get_amount_in_words':self.get_amount_in_words,
                        'get_due_date':self.get_due_date,
                            })
        self.context = context
     
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 

    def get_due_date(self):
        due_date = self.datas['form']['due_date']
        return due_date 
     
    def get_challans(self, data):
        
        challan_list = []
        student_id = self.datas['form']['student_id'][0]
        stu_rec = self.pool.get('sms.student').browse(self.cr ,self.uid , student_id)
        called_challan_book = self.pool.get('sms.transportfee.challan.book').check_transportfee_challans_issued(self.cr, self.uid ,stu_rec.current_class.id ,stu_rec.id)
        print "----",called_challan_book 
        
        challan_ids = self.pool.get('sms.transportfee.challan.book').search(self.cr, self.uid,[('student_class_id','=', stu_rec.current_class.id),
                                                                                                ('student_id','=', stu_rec.id),
                                                                                                ('state','=','fee_calculated')])
        print "====",challan_ids
        if challan_ids:
            rec_challan_ids = self.pool.get('sms.transportfee.challan.book').browse(self.cr, self.uid,challan_ids) 
            for challan in rec_challan_ids:
                challan_dict = {'challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':'','amount_after_due_date':''}
                challan_dict['challan_number'] =  self.get_challan_number(challan.id)
                challan_dict['candidate_info'] = self.get_candidate_info(challan.student_id.id)
                if self.get_on_accounts(challan.id) == []:
                    challan_dict['on_accounts'] =  ' '
                else:
                    challan_dict['on_accounts'] =  self.get_on_accounts(challan.id)
                print self.get_total_amount(challan.id)
                print self.get_amount_in_words(challan.id)
                
                challan_dict['total_amount'] =  self.get_total_amount(challan.id)
                challan_dict['amount_in_words'] =   self.get_amount_in_words(challan.id)
                challan_dict['amount_after_due_date'] = data['form']['amount_after_due_date']
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
     
    def get_vertical_lines_total(self, data):
        line_dots = []
        challan_idd = []
        student_id = self.datas['form']['student_id'][0]
        stu_rec = self.pool.get('sms.student').browse(self.cr ,self.uid , student_id)
        challan_ids = self.pool.get('sms.transportfee.challan.book').search(self.cr, self.uid,[('student_class_id','=',stu_rec.current_class.id),('state','=','fee_calculated')])
        for iddd in challan_ids:
            challan = self.pool.get('sms.transport.fee.challan.lines').search(self.cr, self.uid, [('receipt_book_id','=',iddd)])
            challan_idd.append(challan)
        start = len(challan_idd)
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
            if rec.bank_name1 and rec.bank_acctno1:
                bank= str(rec.bank_name1) + ' - ' +str(rec.bank_acctno1)
            else:
                bank = ''        
        return bank

    def get_banks_2(self):
        banks_ids = self.pool.get('res.company').search(self.cr,self.uid,[])
        banks_recs = self.pool.get('res.company').browse(self.cr,self.uid,banks_ids)
        for rec in banks_recs:
            if rec.bank_name1 and rec.bank_acctno1:
                bank= str(rec.bank_name2) + ' - ' +str(rec.bank_acctno2)
            else:
                bank = ''
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
        student_id = self.datas['form']['student_id'][0]
        stdrec = self.pool.get('sms.student').browse(self.cr ,self.uid , student_id)
        info_dict = {'name':'','father_name':'','class':'','fee_month':''}
        info_dict['name'] = stdrec.name
        info_dict['father_name'] = stdrec.father_name
        info_dict['class'] = stdrec.current_class.name
        fee_month = self.datas['form']['due_date']
        due_date = datetime.strptime(fee_month, '%Y-%m-%d')
        str_date = due_date.strftime('%b %Y')
        info_dict['fee_month'] = str_date
        info_list.append(info_dict)
        return info_list
 
    def get_on_accounts(self, data):
        result = []
        challans = []
        lines_ids = self.pool.get('sms.transport.fee.challan.lines').search(self.cr,self.uid, [('receipt_book_id','=',data)])
        if lines_ids:
            challans = self.pool.get('sms.transport.fee.challan.lines').browse(self.cr,self.uid,lines_ids)
        counter = 1
        for challan in challans:
            if counter <7:
                dict = {'head_name':challan.name,'head_amount':challan.fee_amount}
                result.append(dict)
            counter = counter + 1 
        return result
     
    def get_total_amount(self, data):
        receipt = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data)
        if self.datas['form']['amount_after_due_date']:
            total_amount_str = receipt.total_payables + self.datas['form']['amount_after_due_date'] 
        else:
            total_amount_str = receipt.total_payables
        return total_amount_str
     
    def get_amount_in_words(self,data):
        if self.datas['form']['amount_after_due_date']:
            amount = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data).total_payables + self.datas['form']['amount_after_due_date'] 
        else:   
            amount = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data).total_payables        
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        return return_value
     
report_sxw.report_sxw('report.smstransport_stu_unpaidtransportfee_receipt', 
                      'sms.transport.fee.payments',
                      'addons/smstransport/report/smsfee_unpaid_transportreceipts_report_1o1.rml', 
                      parser=unpaidtransport_fee_challan_parser, 
                      header=None)