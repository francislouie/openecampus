# import pooler
# import time
# import mx.DateTime
# import datetime
# import rml_parse
# from report import report_sxw
# import netsvc
# import locale
# from compiler.ast import Print
# from osv import osv, fields
# import wizard
# import xlwt
# import socket
# import fcntl
# import struct
# from tools import amount_to_text_en
# import babel
# 
# logger = netsvc.Logger()
# result_acc=[]
#     
# class unpaid_fee_challan_parser(rml_parse.rml_parse):
# 
#     def __init__(self, cr, uid, name, context):
# 
#         super(unpaid_fee_challan_parser, self).__init__(cr, uid, name, context)
#         self.result_temp=[]
#         self.localcontext.update( {
#             'get_today':self.get_today,
#             'get_challans':self.get_challans,
#             'get_user_name':self.get_user_name,
#             'get_vertical_lines': self.get_vertical_lines,
#             'get_vertical_lines_total': self.get_vertical_lines_total,
#             'get_banks':self.get_banks,
#             'get_challan_number':self.get_challan_number,
#             'get_candidate_info':self.get_candidate_info,
#             'get_on_accounts':self.get_on_accounts,
#             'get_total_amount':self.get_total_amount,
#             'get_amount_in_words':self.get_amount_in_words,
#          })
#         self.context = context
#     
#     def get_today(self):
#         today = time.strftime('%d-%m-%Y')
#         return today 
#     
#     def get_challans(self, form):
#         challan_list = []
#         
#         for challan in form['challan_ids']:
#             form['challan_id'] = challan 
#             challan_dict = {'banks':'','challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
#             challan_dict['banks'] = self.get_banks(form)
#             challan_dict['challan_number'] = self.get_challan_number(form)
#             challan_dict['candidate_info'] = self.get_candidate_info(form)
#             challan_dict['on_accounts'] = self.get_on_accounts(form)
#             challan_dict['total_amount'] = self.get_total_amount(form)
#             challan_dict['amount_in_words'] = self.get_amount_in_words(form)
#             challan_list.append(challan_dict)
#         return challan_list 
#     
#     def get_user_name(self):
#         user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
#         return   user_name
# 
#     def get_vertical_lines(self, form):
#         line_dots = []
#         for num in range(1,30):
#             dict = {'line-style':'|'}
#             line_dots.append(dict)
#         return line_dots
#     
#     def get_vertical_lines_total(self, form):
#         line_dots = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         start = len(challan.challan_heads)
#         if start >=14:
#             dict = {'line-style':'|'}
#             line_dots.append(dict)
#         else:
#             for num in range(start,14):
#                 dict = {'line-style':'|'}
#                 line_dots.append(dict)
#         return line_dots    
#     
#     def get_banks(self, form):
#         banks = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         for category in challan.challan_banks:
#             dict = {'bank_name':category.name.name}
#             banks.append(dict) 
#         return banks
# 
#     def get_challan_number(self, form):
#         line_dots = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         challan_str = str(challan.challan_no)
#         return challan_str.split("-")[1] + " (" + challan_str.split("-")[0]+ ")"
# 
#     def get_candidate_info(self, form):
#         info_list = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         info_dict = {'name':'','father_name':'','program':'','semester':''}
#         
#         if challan.challan_for == 'Student':
#             info_dict['name'] = challan.student.name
#             info_dict['father_name'] = challan.student.father_name
#             info_dict['program'] = challan.program.name
#             info_dict['semester'] = challan.semester.semester_academic_calender.name
#         else:
#             employee = self.pool.get('hr.employee').browse(self.cr,self.uid,challan.employee.id)
#             info_dict['name'] = employee.name
#             info_dict['father_name'] = employee.father_name
#             info_dict['program'] = 'Employee'
#             info_dict['semester'] = 'Employee'
#         
#         info_list.append(info_dict)
#         return info_list
# 
#     def get_on_accounts(self, form):
#         banks = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         for challan_head in challan.challan_heads:
#             dict = {'head_name':challan_head.name.title,'head_amount':babel.numbers.format_currency((challan_head.amount), "" )}
#             banks.append(dict) 
#         return banks
#     
#     def get_total_amount(self, form):
#         line_dots = []
#         challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id'])
#         total_amount_str = str(babel.numbers.format_currency((challan.total_amount), "" )) + " /="
#         return total_amount_str
#     
#     def get_amount_in_words(self,form):
#         amount = challan = self.pool.get('cms.challan').browse(self.cr,self.uid,form['challan_id']).total_amount
#         user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
#         cur = user_id.company_id.currency_id.name
#         amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
#         return_value=str(amt_en).replace('Cent','Paisa')
#         return return_value
#     
# report_sxw.report_sxw('report.smsfee_unpaidfee_receipt_name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_unpaid_receipts_report.rml',parser = unpaid_fee_challan_parser, header=None)
