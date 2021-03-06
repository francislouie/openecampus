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
     
"""This is the main parsor that prints challans for academics and transport with 1 student per page 
   class wise, other parsers that prints class wise challans, should be rmeoved """

class report_unpaid_fee_bills_3folded(report_sxw.rml_parse):
    #this will be the only challans parsser called for
    # acadimc fee, transport fee and other 
    # currently called for clasess wside fees for trasport and academics
    # later on will be adjusted to call the same parser for sing student challan prrintg both in academcis and transport 
    #calling tested by shahid on 29 DEC
    #1 called by academics challns of whole class wizard [yes]
    #2 Called by transport cchallans of whole class same wizard [yes]
    #3 called by individual student  Academic challan [Yes]
    #4 Called by individual student Transpor same wizard [Yes]
 
    def __init__(self, cr, uid, name, context):

        super(report_unpaid_fee_bills_3folded, self).__init__(cr, uid, name, context)
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
            'get_due_date_str':self.get_due_date_str,
            'get_class_group':self.get_class_group,
            'get_challan_logo':self.get_challan_logo,
            'get_challan_header_lineone':self.get_challan_header_lineone,
            'get_challan_header_linetwo':self.get_challan_header_linetwo,
            'get_challan_header_linethree':self.get_challan_header_linethree,
            'get_challan_footer_one':self.get_challan_footer_one,
            'get_challan_footer_two':self.get_challan_footer_two,
            'get_department_logo':self.get_department_logo,
            # 'get_vechil_no':self.get_vechil_no,
            
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
        
        # rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        # if len(rescompany_id)>1:
        #      return ''
        # company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        if self.datas['form']['category'] == 'Academics':
            # query_for_individual_student='select current_class from sms_student where id=""" + str(self.datas['form']['student_id'][0]) + """)"
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


        # line1 = company_recs[0].company_cfieldone
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
        # company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
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
            # line2 = company_recs[0].company_cfieldtwo_trans
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
        # rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------        
        # if len(rescompany_id)>1:
        #     return ''

        # company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)
        if self.datas['form']['category']== 'Academics':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldfour
                               from sms_academics_session where
                              id = (
                                               select acad_session_id from sms_academiccalendar where id=(
                                               select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line4 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldfour
                                               from sms_academics_session where
                                              id = ( select acad_session_id from sms_academiccalendar where
                                                     id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line4 = self.cr.fetchone()[0]
            # line4 = company_recs[0].company_cfieldfour
        elif self.datas['form']['category'] == 'Transport':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldfour_trans
                               from sms_academics_session where
                              id = (
                                               select acad_session_id from sms_academiccalendar where id=(
                                               select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line4 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldfour_trans
                                               from sms_academics_session where
                                              id = ( select acad_session_id from sms_academiccalendar where
                                                     id=""" + str(self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line4 = self.cr.fetchone()[0]
            # line4 = company_recs[0].company_cfieldfour_trans
        return line4
    
    def get_challan_footer_two(self):
        # rescompany_id = self.pool.get('res.company').search(self.cr, self.uid,[])
        # #-------------Handling Only one Company is There are multiple companies blank space will be returned----------------
        # if len(rescompany_id)>1:
        #     return ''

        # company_recs = self.pool.get('res.company').browse(self.cr, self.uid, rescompany_id)

        if self.datas['form']['category']== 'Academics':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldfive
                                          from sms_academics_session where
                                         id = (
                                                          select acad_session_id from sms_academiccalendar where id=(
                                                          select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line5 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldfive
                                                          from sms_academics_session where
                                                         id = ( select acad_session_id from sms_academiccalendar where
                                                                id=""" + str(
                    self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line5 = self.cr.fetchone()[0]
            # line5 = company_recs[0].company_cfieldfive
        elif self.datas['form']['category'] == 'Transport':
            if 'student_id' in self.datas['form']:
                query = """select company_cfieldfive_trans
                                          from sms_academics_session where
                                         id = (
                                                          select acad_session_id from sms_academiccalendar where id=(
                                                          select current_class from sms_student where id=""" + str(
                    self.datas['form']['student_id'][0]) + """))"""
                self.cr.execute(query)
                line5 = self.cr.fetchone()[0]
            else:
                query = """select company_cfieldfive_trans
                                                          from sms_academics_session where
                                                         id = ( select acad_session_id from sms_academiccalendar where
                                                                id=""" + str(
                    self.datas['form']['class_id'][0]) + """)"""
                self.cr.execute(query)
                line5 = self.cr.fetchone()[0]
            # line5 = company_recs[0].company_cfieldfive_trans
        return line5
     
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 

    def get_due_date(self):
        due_dat = self.datas['form']
        due_date = self.datas['form']['due_date']
        print 'This is the Due date------------------',due_dat
        due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        if 'student_id' in self.datas['form']:
            class_id = self.pool.get('sms.student').browse(self.cr,self.uid,self.datas['form']['student_id'][0]).current_class.id
        else:
            class_id = self.datas['form']['class_id'][0]
        aca_cal_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,class_id)
        remove_due_date = aca_cal_obj.acad_session_id.remove_due_date
        print"remove_due_date",remove_due_date
        if remove_due_date ==True:
            due_dat = ''
        else:
            due_dat = due_date
        return due_dat
    
    
    
    def get_due_date_str(self):
        if 'student_id' in self.datas['form']:
            print("fordata",self.datas['form'])
            #user is printing indivual student challan from student form, get class id using student id from wizard form
            class_id = self.pool.get('sms.student').browse(self.cr,self.uid,self.datas['form']['student_id'][0]).current_class.id
        else:
            class_id = self.datas['form']['class_id'][0]
        aca_cal_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, class_id)
        remove_due_date = aca_cal_obj.acad_session_id.remove_due_date
        print"remove_due_date",remove_due_date
        if remove_due_date ==True:
            due_date = ''
        else:
            due_date = 'Due date :'
        return due_date 

    def get_class_group(self, data):
        if 'student_id' in self.datas['form']:
            print("fordata",self.datas['form'])
            #user is printing indivual student challan from student form, get class id using student id from wizard form
            cls_id = self.pool.get('sms.student').browse(self.cr,self.uid,self.datas['form']['student_id'][0]).current_class.id
        else:
            cls_id = self.datas['form']['class_id'][0]
        class_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid, cls_id)
        return class_obj.group_id.name  

    def get_challans(self, data):
        #currentlty this parser is set to call for whole class challans orinting
        #both transport and acadmics
        #later on this will be set to call this parser for single students also, both academics challans and transprot challans (3-10-2017)
        
        challan_list = []
        ###########print challan at the time of admission for paying fee (it is before admitting student)
        if data['model'] == 'student.admission.register':
            tlt_amount = 0
            rec = self.pool.get('student.admission.register').browse(self.cr,self.uid,data['active_ids'] )
            info_dict = {'name':rec.name,'father_name':rec.father_name,'Class':rec.student_class.name,'semester':''}
            fee_res = []
            challan_dict = {'challan_number':'','candidate_info':'','on_accounts':'','total_amount':'','amount_in_words':''}
            for fee in rec.fee_ids  :
                fee_name = str(fee.name.name)+"  "+str(fee.fee_month.name)
                dict = {'head_name':fee_name,'head_amount':fee.amount}
                fee_res.append(dict)
                tlt_amount = tlt_amount+fee.amount
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
           #check if printed via student form
             if 'student_id' in self.datas['form']:

                #challan is being printed via student form, canlcel all other challans of this sutdent
                challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid,[('challan_cat','=',self.datas['form']['category']),('student_id','=',self.datas['form']['student_id'][0]),('state','=','fee_calculated')])
             else:
                challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid, [('challan_cat', '=', self.datas['form']['category']),('student_class_id', '=', self.datas['form']['class_id'][0]), ('state', '=', 'fee_calculated')])
        if challan_ids:
                rec_challan_ids = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid,challan_ids) 
                for challan in rec_challan_ids:

                    challan_dict = {'challan_number':'','candidate_info':'','on_accounts':'','vertical_lines':'','total_amount':'',
                                'amount_in_words':'','amount_after_due_date':'','dbid':'','grand_total':'','grand_lable':'','partial_lable':'' ,'Table_1':''
                                ,'vechil_no':'','driver_name':'','vechil_name':''}
                    challan_dict['challan_number'] = self.get_challan_number(challan.id)
                    challan_dict['candidate_info'] = self.get_candidate_info(challan.student_id.id)
                    challan_dict['on_accounts'] = self.get_on_accounts(challan.id)
                    challan_dict['vertical_lines'] = self.get_vertical_lines_total(challan.id)
                    challan_dict['total_amount'] = self.get_total_amount(challan.id)
                    challan_dict['amount_in_words'] = self.get_amount_in_words(challan.id) 
                    challan_dict['dbid'] = self.print_challan_dbid(challan.id)
                    challan_dict['total_amount'] = self.get_total_amount(challan.id)
                    #adding vechil No phase no and driver number to transport challans this will work for Individual
                    #as well as class wise challans
                    if self.datas['form']['category'] == 'Transport':
                        query = """ select vehcile_no,name,driver from  sms_transport_vehcile
                                       where id =(select vehcile_reg_students_id from sms_student where id=""" \
                                + str(challan.student_id.id) + """)"""
                        self.cr.execute(query)
                        _result1 = self.cr.fetchall()
                        if len(_result1) > 0:
                            _result2 = _result1[0]
                            veh_reg_obj = self.pool.get('res.partner').browse(self.cr,self.uid,_result2[2])
                            challan_dict['vechil_no'] = "Vehcile No:"+str(_result2[0])
                            challan_dict['vechil_name'] = "Vehcile Name: "+str(_result2[1])
                            challan_dict['driver_name'] = "Driver Name: "+str(veh_reg_obj.name)
                        else:
                            challan_dict['vechil_no'] = '--'
                            challan_dict['vechil_name'] = '--'
                            challan_dict['driver_name'] = '--'


                        if 'fee_receiving_type' in self.datas['form']:
                                if self.datas['form']['fee_receiving_type'] == "Partial":
                                    grand_amt=self.pool.get('sms.student').total_outstanding_dues(self.cr, self.uid, self.datas['form']['student_id'][0], self.datas['form']['category'],'fee_unpaid')
                                    total_amt=self.get_total_amount(challan.id)
                                    dues=int(grand_amt)-int(total_amt)
                                    challan_dict['Table_1'] = "Table_1"
                                    challan_dict['grand_lable']="Dues:"
                                    challan_dict['grand_total']=" G.T ("+str(grand_amt)+") - P.T ("+str(total_amt)+") ="+str(dues)
                                    challan_dict['partial_lable']='Partial Challan'
                        # color  #D4D4D4 [record['partial_lable']challan_dict['partial_lable']='Partial Challan'

                    if self.datas['form']['amount_after_due_date']:
                        challan_dict['amount_after_due_date'] = challan_dict['total_amount'] + self.datas['form']['amount_after_due_date'] 
                    else:
                        challan_dict['amount_after_due_date'] = data['form']['amount_after_due_date']
                    challan_list.append(challan_dict)
        return challan_list  
     
    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return   user_name

    def get_vechil_no(self):
        if self.datas['form']['category'] == 'Academics':
            vechil_no = None
        elif self.datas['form']['category'] == 'Transport':
            if 'student_id' in self.datas['form']:
                std_id = str(self.datas['form']['student_id'][0])
                query = """ select vehcile_reg_students_id from sms_student where id=""" + std_id
                self.cr.execute(query)
                vechil_no = self.cr.fetchone()[0]
            else:
                std_id = str(self.datas['form']['student_id'][0])
                query = """ select vehcile_reg_students_id from sms_student where current_class="""\
                        +str(self.datas['form']['class_id'][0])
                self.cr.execute(query)
                vechil_no = self.cr.fetchone()[0]
        print('vechil_no',vechil_no)
        return vechil_no


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
        challan_ids = self.pool.get('smsfee.receiptbook').search(self.cr, self.uid,[('id','=',data)])
        challan_rec = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid,challan_ids)
        challan =  challan_rec[0].counter or str(challan_rec[0].id)+"*****"
        return challan
 
    def get_candidate_info(self, data):
        info_list = []
        stdrec = self.pool.get('sms.student').browse(self.cr, self.uid, data)
        remove_fee_title =stdrec.current_class.acad_session_id.remove_fee_title
        
        info_dict = {'name':'','father_name':'','class':'','fee_month':'','fee_mon_str':'','reg_no':''}
        info_dict['reg_no'] = stdrec.registration_no 
        info_dict['name'] = stdrec.name 
        info_dict['father_name'] = stdrec.father_name
        info_dict['class'] = stdrec.current_class.class_id.name + " - " + stdrec.current_class.section_id.name + " " + stdrec.current_class.class_session
        fee_month = self.datas['form']['due_date']
        due_date = datetime.strptime(fee_month, '%Y-%m-%d')
        str_date = due_date.strftime('%b %Y')
        if remove_fee_title ==True:
            fee_mon_str = ''
            fee_month = ''
        else:
            fee_mon_str = 'Fee Month:'
            fee_month = str_date
        info_dict['fee_mon_str'] = fee_mon_str
        info_dict['fee_month'] = fee_month
        info_list.append(info_dict)
        return info_list
 
    def get_on_accounts(self, data):
        result = []
        lines_ids = self.pool.get('smsfee.receiptbook.lines').search(self.cr, self.uid, [('receipt_book_id','=',data)])
        if lines_ids:
            challans = self.pool.get('smsfee.receiptbook.lines').browse(self.cr, self.uid, lines_ids)
            if len(lines_ids)>10:
                title = ''
                whole_amount = 0
                for challan in challans:

                    title += str(challan.fee_type.name) +':'+str(challan.fee_amount)+','
                    whole_amount = int(whole_amount) + int(challan.fee_amount)
                    
                print'-------------------'+title
                dict = {'head_name':title,'head_amount':whole_amount}
                
                result.append(dict) 
            else:
                for challan in challans:
                    if 'student_id' in self.datas['form']:
                        class_id = self.pool.get('sms.student').browse(self.cr,self.uid,self.datas['form']['student_id'][0]).current_class.id
                    else:
                        class_id = self.datas['form']['class_id'][0]
                    aca_cal_obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,class_id)
                    remove_fee_title = aca_cal_obj.acad_session_id.remove_fee_title
                    print"remove_fee_titlet",remove_fee_title
                    if remove_fee_title ==True:
                        titl = challan.fee_type.name

                    else:
                        titl = challan.fee_name 
                    dict = {'head_name':titl,'head_amount':challan.fee_amount}

                    result.append(dict) 
        return result
    
    def print_challan_dbid(self, data):
        return data
     
    def get_total_amount(self, data):
        receipt = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid, data)
        total_amount_str = receipt.total_paybles
        return total_amount_str
     
    def get_amount_in_words(self,data):
        amount = self.pool.get('smsfee.receiptbook').browse(self.cr,self.uid,data).total_paybles        
        user_id = self.pool.get('res.users').browse(self.cr, self.uid,[self.uid])[0]
        cur = user_id.company_id.currency_id.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return_value=str(amt_en).replace('Cent','Paisa')
        return return_value
     

report_sxw.report_sxw('report.smsfee_print_one_student_per_page', 'smsfee.classfees.register', 'addons/smsfee/report_unpaid_fee_bills_3folded.rml',parser = report_unpaid_fee_bills_3folded, header=None)
