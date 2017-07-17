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
            'get_challan_number':self.get_challan_number,
            'get_candidate_info':self.get_candidate_info,
            'get_on_accounts':self.get_on_accounts,
            'get_total_amount':self.get_total_amount,
            'get_amount_in_words':self.get_amount_in_words,
            'get_due_date':self.get_due_date,
            'get_class_group':self.get_class_group,
            'get_challan_logo':self.get_challan_logo,
            'get_challan_header_lineone':self.get_challan_header_lineone,
            'get_challan_header_linetwo':self.get_challan_header_linetwo,
            'get_challan_header_linethree':self.get_challan_header_linethree,
            'get_challan_footer_one':self.get_challan_footer_one,
            'get_challan_footer_two':self.get_challan_footer_two,
         })
        self.context = context

    def get_challan_logo(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            logo = rec.company_clogo
        return logo

    def get_challan_header_lineone(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            fieldone = rec.company_cfieldone
        return fieldone

    def get_challan_header_linetwo(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            fieldtwo = rec.company_cfieldtwo
        return fieldtwo
    
    def get_challan_header_linethree(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            fieldthree = rec.company_cfieldthree
        return fieldthree
    
    def get_challan_footer_one(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            footerone = rec.company_cfieldfour
        return footerone
    
    def get_challan_footer_two(self):
        rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        if len(rescompany_id)>1:
            return ''
        company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        for rec in company_recs:
            footertwo = rec.company_cfieldfive
        return footertwo
     
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 

    def get_due_date(self):
        due_date = self.datas['form']['due_date']
        due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return due_date 

    def get_class_group(self, data):
        cls_id = self.datas['form']['class_id'][0]
        class_id = self.pool.get('sms.academiccalendar').search(self.cr, self.uid, [('id','=',cls_id)])
        class_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, class_id)
        for obj in class_obj:
            group = obj.group_id.name
        return group  
     
    def get_challans(self, data):
        
        challan_list = []
        if data['model'] == 'student.admission.register':
            tlt_amount = 0
            rec = self.pool.get('student.admission.register').browse(self.cr,self.uid,data['active_ids'] )
            info_dict = {'name':rec.name,'father_name':rec.father_name,'Class':rec.student_class.name,'semester':''}
            
            fee_res = []
            challan_dict = {'banks_1':'','challan_number_1':'','candidate_info_1':'','on_accounts_1':'','total_amount_1':'','amount_in_words_1':'',
                            'banks_2':'','challan_number_2':'','candidate_info_2':'','on_accounts_2':'','total_amount_2':'','amount_in_words_2':''}
            i = 0
            for fee in rec.fee_ids  :
                if (i % 2) == 0:
                    index = 2
                else:
                    index = (i % 2)
                    
                fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
                dict = {'head_name':fee_name,'head_amount':fee.amount}
                fee_res.append(dict)
                tlt_amount = tlt_amount+fee.amount
                
                challan_dict['challan_number_'+ str(index)]  = rec.registration_no
                challan_dict['candidate_info_'+ str(index)] =  [info_dict]
                challan_dict['on_accounts_'+ str(index)] = fee_res
                challan_dict['total_amount_'+ str(index)] = tlt_amount
                
                if i % 2 == 0:
                    challan_list.append(challan_dict)
                    challan_dict = {'banks_1':'','challan_number_1':'','candidate_info_1':'','on_accounts_1':'','total_amount_1':'','amount_in_words_1':'',
                                    'banks_2':'','challan_number_2':'','candidate_info_2':'','on_accounts_2':'','total_amount_2':'','amount_in_words_2':''}
                i = i + 1
                
            if (i-1) % 2 != 0:
                challan_list.append(challan_dict)
                
            #*******************convert the amount in text form****************************
            user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
            cur = user_id.company_id.currency_id.name
            amt_en = amount_to_text_en.amount_to_text(tlt_amount,'en',cur);
            return_value=str(amt_en).replace('Cent','Paisa')
            #*******************************************************************************
            
            challan_dict['amount_in_words'] = return_value
            challan_list.append(challan_dict)                     
        else:
            
            cls_id = self.datas['form']['class_id'][0]
            challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid,[('student_class_id','=',cls_id),('state','=','fee_calculated')]) 
            if challan_ids:
                i = 0
                challan_dict = {'challan_number_1':'','candidate_info_1':'','vertical_lines_1':'','on_accounts_1':'','total_amount_1':'','amount_in_words_1':'','amount_after_due_date_1':'',
                                'challan_number_2':'','candidate_info_2':'','vertical_lines_2':'','on_accounts_2':'','total_amount_2':'','amount_in_words_2':'','amount_after_due_date_2':''}
                
                rec_challan_ids = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid, challan_ids) 
                for challan in rec_challan_ids:
                    if (i % 2) == 0:
                        index = 2
                    else:
                        index = (i % 2)
                    challan_dict['challan_number_'+ str(index)] = self.get_challan_number(challan.id)
                    challan_dict['candidate_info_'+ str(index)] = self.get_candidate_info(challan.student_id.id)
                    challan_dict['on_accounts_'+ str(index)] = self.get_on_accounts(challan.id)
                    challan_dict['vertical_lines_'+ str(index)] = self.get_vertical_lines_total(challan.id)
                    challan_dict['total_amount_'+ str(index)] = self.get_total_amount(challan.id)
                    challan_dict['amount_in_words_'+ str(index)] = self.get_amount_in_words(challan.id)
                    if self.datas['form']['amount_after_due_date']:
                        challan_dict['amount_after_due_date_'+str(index)] = challan_dict['total_amount_'+str(index)] + self.datas['form']['amount_after_due_date'] 
                    else:
                        challan_dict['amount_after_due_date_'+str(index)] = data['form']['amount_after_due_date']
                    if i % 2 == 0:
                        challan_list.append(challan_dict)
                        challan_dict = {'challan_number_1':'','candidate_info_1':'','vertical_lines_1':'','on_accounts_1':'','total_amount_1':'','amount_in_words_1':'','amount_after_due_date_1':'',
                                        'challan_number_2':'','candidate_info_2':'','vertical_lines_2':'','on_accounts_2':'','total_amount_2':'','amount_in_words_2':'','amount_after_due_date_2':''}
                    i = i + 1

                if (i-1) % 2 != 0:
                    challan_list.append(challan_dict)
        return challan_list  
     
    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return user_name
 
    def get_vertical_lines(self, data):
        line_dots = []
        for num in range(1,30):
            dict = {'line-style':'|'}
            line_dots.append(dict)
        return line_dots
     
    def get_vertical_lines_total(self, data):
        line_dots = []
        lines_ids = self.pool.get('smsfee.receiptbook.lines').search(self.cr,self.uid, [('receipt_book_id','=',data)])
        if lines_ids:
            challans = self.pool.get('smsfee.receiptbook.lines').browse(self.cr,self.uid, lines_ids)
            start = len(challans)
            if start >=11:
                dict = {'line-style':'|'}
                line_dots.append(dict)
            else:
                for num in range(start,11):
                    dict = {'line-style':'|'}
                    line_dots.append(dict)
        return line_dots    
     
    def get_challan_number(self, data):
        challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid, [('id','=', data)])
        challan_rec = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid, challan_ids)
        challan =  challan_rec[0].counter or str(challan_rec[0].id)+"*****"
        return challan
 
    def get_candidate_info(self, data):
        info_list = []
        stdrec = self.pool.get('sms.student').browse(self.cr, self.uid, data)
        info_dict = {'name':'','father_name':'','class':'','fee_month':'','reg_no':''}
        info_dict['reg_no'] = stdrec.registration_no 
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
        lines_ids = self.pool.get('smsfee.receiptbook.lines').search(self.cr,self.uid, [('receipt_book_id','=',data)])
        if lines_ids:
            challans = self.pool.get('smsfee.receiptbook.lines').browse(self.cr,self.uid,lines_ids)
        for challan in challans:
            dict = {'head_name':challan.fee_name,'head_amount':challan.fee_amount}
            result.append(dict) 
        return result
     
    def get_total_amount(self, data):
        receipt = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data)
        if self.datas['form']['amount_after_due_date']:
            total_amount_str = receipt.total_paybles + self.datas['form']['amount_after_due_date'] 
        else:
            total_amount_str = receipt.total_paybles
        return total_amount_str
     
    def get_amount_in_words(self,data):
        amount = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data).total_paybles        
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        return return_value
     
report_sxw.report_sxw('report.smsfee_print_three_student_per_page', 'smsfee.classfees.register', 'addons/smsfee/smsfee_unpaid_receipts_report_3o1.rml',parser = unpaid_fee_challan_parser, header=None)
