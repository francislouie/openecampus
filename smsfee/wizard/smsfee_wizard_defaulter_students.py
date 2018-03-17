from openerp.osv import fields, osv
import datetime
import xlwt
import locale
from datetime import datetime
#from osv import osv
from reportlab.pdfgen import canvas
import sys
import subprocess
import time
import urllib
#import netifaces 
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from xml.etree import ElementTree
import os
from openerp.osv.orm import browse_record

class fee_defaulters(osv.osv_memory):
    """
    This wizard was initially developed for printing defaulter students list only, now we are using this for fee analysis purpose, other reports 
    are also added to this, later on its name will be change in .py and xml file
    --last updated: 31 DEC 17 by Shahid
    """
    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
    
    _name = "fee.defaulters"
    _description = "Prints defaulter list"
    _columns = {
              "session": fields.many2one('sms.session', 'Session', help="Select A session , you can also print reprts from previous session."),
              "class_id": fields.many2many('sms.academiccalendar','sms_academiccalendar_class_fee', 'thisobj_id', 'academiccalendar_id','Class', domain="[('session_id','=',session)]"),
              "fee_type_list": fields.many2many('smsfee.feetypes','fee_defaulters_feetype_rel','fee_defaulters_id','smsfee_feetypes_id','SS'),
              'report_type': fields.selection([('summary','Print Summary (Donot show monthly Details'),('detailed','Detailed Report')],'Options'),
              'category':fields.selection([('Academics','Academics'),('Transport','Transport'),('All','All Fee Categories')],'Fee Category'),
              'order_by':fields.selection([('sms_student.name','Student Name'),('sms_student.registration_no','Registration No'),('sms_student.state','Admission Status'),('sms_academiccalendar.name,sms_student.name','Class')],'Order By'),
              'show_phone_no':fields.boolean('Display Contact No'),
              'developer_mode':fields.boolean('For Developer'),
              'base_amount':fields.integer('Dues Greater Than',help = 'Enter an amount e.g 1000, it will search all students having dues greater or equal to 1000.')
               }
    _defaults = {
                 'session':_get_active_session,
                 'category':'Academics',
                 'base_amount':1,
                 'order_by':'sms_student.registration_no',
           }
    
    def print_defaulter_summary(self, cr, uid, ids, data):
        result = []
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee_defaulter_studnent_list_name',
            'datas': datas,
        }
    
    def print_fee_analysis_ms_excel(self, cr, uid, ids, data):
        print("print_fee_analysis_ms_excel called")
       
      
        result = []
        book=xlwt.Workbook()
        header_top =  xlwt.Style.easyxf('font: bold 0, color white,  height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour gray80;'
                             )
                 
        header_feetypes = xlwt.Style.easyxf('font: bold 0, color white, , height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_blue;'
                             )
        header_months = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_green;'
                             )
         
        student_white_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white;'
                             )
        student_grey_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  gray25 ;'
                             )
        paid_fee = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white;'
                             )
        unpaid_fee = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders:top_color red, bottom_color red, right_color red, left_color red,\
                              left thin, right thin, top thin, bottom thin;'
                             'pattern: pattern solid, fore_colour  white;'
                             'font: color red'
                             )
        
        selected_fee_list=[]
        for f in self.browse(cr, uid, ids):
            if not f.fee_type_list:
               raise osv.except_osv(('Please Select Fee'), ('Defaulter Excel Report Fees to be included'))
            for s in f.fee_type_list:
                selected_fee_list.append(s.id)     
        #classes = self.pool.get('sms.academiccalendar').browse(cr,uid,41)
       
         
        #loop via classes, for each class there will be 1 sheet
         
        collected_classes = []
        for f in self.browse(cr, uid, ids):
            if f.class_id:
                for cls2 in f.class_id:
                    collected_classes.append(cls2.id)
                 
#                 sql1 = """SELECT id,name from sms_academiccalendar where id in"""  +str(collected_classes +"""" ORDER BY name """
#                 cr.execute(sql1)
#                 classes = cr.fetchall()
                classes = self.pool.get('sms.academiccalendar').browse(cr,uid,collected_classes)
                class_ctr = 1
                row = 0
                for this_class in classes:
                    print("this_class.name",this_class.name)
                     
                    sheet1=book.add_sheet(str(class_ctr)+" "+str(this_class.class_id.name),cell_overwrite_ok=True)
                    title = this_class.class_id.name
                    class_ctr = class_ctr + 1
                    _col = (sheet1.col(0)).width = 200 * 15
                    _col = (sheet1.col(1)).width = 300 * 15
                    _col = (sheet1.row(2)).height = 300 * 15
                    _col = (sheet1.row(2)).height = 200 * 15
                     
                    sheet1.write(3,0,'Rego NO',header_top)
                    sheet1.write(3,1,'Name',header_top)
                     
                    #Find all fee types of this class and arrange in one reow of excel #changes: added subtype in select query
                    sqlfees = """ SELECT smsfee_feetypes.id,smsfee_feetypes.name,  
                                CASE
                                  WHEN (subtype != 'Monthly_Fee') THEN '01'
                                  WHEN (subtype= 'Monthly_Fee') THEN '02'
                                  ELSE '00'
                                 END AS sequence_no
                                from smsfee_feetypes
                                where  smsfee_feetypes.category = '"""+str(f.category)+ """'
                                ORDER BY sequence_no,smsfee_feetypes.name """         # changes: interchanged category.name and seq no
 
                    cr.execute(sqlfees)
                    feerec = cr.fetchall()
                    col_fee = 2# this is the column no in sheet for fee header
                    fee_ids_list = []
                    month_dict_ids={}
                    adm_dict_ids={}
                    annual_dict_ids={}
                    feerec2=[]
                    for feere in feerec:
                        for  id in selected_fee_list:
                            if id ==feere[0]:
                               feerec2.append(feere)
                               
                   
                    for fee in feerec2:
                        fee_ids_list.append(fee[0])
                        print("this_class",this_class,"this_class.session_id",this_class.session_id,"/nthis_class.session_id.id",this_class.session_id.id)
                        
                        sql3 = """SELECT id,name from sms_session_months where session_id  = """+str(this_class.session_id.id)+""" order by session_year, to_date(name,'Month') """
                        cr.execute(sql3)
                        months = cr.fetchall()
                        annual_number=4
                        #testing git branch 2
                        if fee[0] ==2:
                            if fee[0]==2:
                                month_ids_list = []
                                for this_month in months:
                                    if f.developer_mode:                                
                                        ft_name = str(fee[1])+"\n"+str(this_month[1])+"\nmonth_id:"+str(this_month[0])+"\nfee_id:"+str(fee[0])
                                    else:
                                        ft_name=str(fee[1])+"\n"+str(this_month[1])[:3].upper()+str(this_month[1])[-5:]
                                    sheet1.write_merge(r1=0, c1=0, r2=2, c2=11)
                                    _col = (sheet1.row(col_fee)).height = 100 * 10
                                    #cell width for fee type other than months
                                    _col = (sheet1.col(col_fee)).width = 400 * 20
                                    sheet1.write(0,2, title,header_top )
                                    sheet1.write(3,col_fee,ft_name,header_feetypes)
                                    month_ids_list.append(this_month[0])
                                    month_dict_ids[this_month[0]+fee[0]]=col_fee
                                    col_fee = col_fee +1
                             
                        else:
                            annual_dict_ids[fee[0]]=col_fee
                            annual_number=annual_number+1
                            sheet1.write_merge(r1=0, c1=0, r2=2, c2=11)
                            _col = (sheet1.row(col_fee)).height = 100 * 10
                            _col = (sheet1.col(col_fee)).width = 200 * 20
                            sheet1.write(0,2, title,header_feetypes )
                            if f.developer_mode:
                                ft_name = str(fee[1])+"\nfee_id:"+str(fee[0])
                            else:
                                ft_name=str(fee[1])
                            sheet1.write(3,col_fee,ft_name,header_feetypes )
                            #popluate dict1 for non mnthly fees
                            col_fee = col_fee +1
                             
                     
                    #get students for selected class
                    print "total "+str(fee_ids_list)+ " fee ids in fee_ids_list"
                    print("this_class_id ",this_class.id)
                    sql4 = """ SELECT id,registration_no, name,state from sms_student where current_class= """+str(this_class.id)+ """ 
                               order by registration_no,name """
                    cr.execute(sql4)
                    students = cr.fetchall()
                    row = 4
                    color=True
                    #set column again to start iele left most 
                    for this_student in students:
                        color=not color 
             
                        _col = (sheet1.col(1)).width = 200 * 10
                        _col = (sheet1.col(1)).height = 200 *10
                        _col = (sheet1.row(row)).height = 100 * 10
                        
                        if color:
                            sheet1.write(row,0, this_student[1],student_grey_rows )
                            sheet1.write(row,1, this_student[2],student_grey_rows )
                        else:
                            sheet1.write(row,0, this_student[1],student_white_rows )
                            sheet1.write(row,1, this_student[2],student_white_rows )
                       # print("student id",this_student[0],"\nmonth ids",month_ids_list ,"\nfee ids",fee_ids_list )
                        #now loop via the fees dictionaru for this student
                        col_fee = 2
                        col_month=25
                        col_adminiistrative=13
                         
                        for fees2 in fee_ids_list:
                           
                            if 2 in selected_fee_list:
                                for month2 in month_ids_list:
                                    sql5 = """select id,fee_month,fee_amount,generic_fee_type,state,receipt_no,date_fee_paid
                                                  from smsfee_studentfee where student_id =  """+str(this_student[0])+"""
                                              and generic_fee_type= """+str(fees2)+""" and fee_month="""+str(month2)
                                   
                                    cr.execute(sql5)
                                    stdfee = cr.fetchall()
                                    print("stdfee",stdfee)
                                    for found_fee in stdfee:
                                        #print( "generic fee type",fees2,"fee_month",month2,"this_student",this_student[0])
                                        if found_fee[3]==2:
                                            if found_fee[4]=='fee_paid':
                                                if f.developer_mode:
                                                    label = 'Paid Amount:\n'+str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3]) +'\n'+'Bill No:'+str(found_fee[5])+'Paid On :\n'+str(found_fee[6])
                                                    print 'labellll',label
                                                else:
                                                    label='Paid Amount:\n'+str(found_fee[2])+'\nBill No:'+str(found_fee[5]) +'\nPaid On:'+str(found_fee[6])
                                                sheet1.write(row,month_dict_ids[month2+fees2], label,paid_fee)
                                                col_month = col_month + 1
                                                col_fee=col_fee+1
                                            else:
                                                if f.developer_mode:
                                                    label = 'Fee Amount:\n'+str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                                else:
                                                    label='Fee Amount\n'+str(found_fee[2]) 
                                                sheet1.write(row,month_dict_ids[month2+fees2], label,unpaid_fee)
                                                col_month = col_month + 1
                                                col_fee=col_fee+1
                                           
                                             
                                                
                                        else:
                                            if found_fee[4]=='fee_paid':
                                                if f.developer_mode:
                                                    label = 'Paid Amount:\n'+str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                                else:
                                                    label='Paid Amount:\n'+str(found_fee[2])+'\nBill No:'+str(found_fee[5]) +'\nPaid On:'+str(found_fee[6])
                                                sheet1.write(row,annual_dict_ids[fees2], label,student_white_rows)
                                            else:
                                                if f.developer_mode:
                                                    label = 'Fee Amount:\n'+str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                                else:
                                                    label='Fee Amount:\n '+str(found_fee[2]) 
                                                sheet1.write(row,annual_dict_ids[fees2], label,student_white_rows)
                                                
                                      # if found_fee[3] !='02':
                                       #  sheet1.write(row,annual_dict_ids[fees2[0]], label,student_rows)
                                                     
                                             
     
                                        #    print("found fee",found_fee ,"\nsearch on ______generic id____",fees2,"\nthis_student.......",this_student[0],"\nmonth",month2)
                                        #
                                         #   label = str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                          #  print "label:",label
                                           # sheet1.write(row,col_fee, label,student_rows)
                                            col_fee = col_fee + 1
                            else:
                                
                                sql6 = """select id,fee_month,fee_amount,generic_fee_type,state
                                              from smsfee_studentfee where student_id =  """+str(this_student[0])+"""
                                          and generic_fee_type= """+str(fees2)
                               
                                cr.execute(sql6)
                                stdfee = cr.fetchall()
                                for found_fee in stdfee:
                                    #print( "generic fee type",fees2,"fee_month",month2,"this_student",this_student[0])
                                    if found_fee[3]==2:
                                        if found_fee[4]=='fee_paid':
                                            if f.developer_mode:
                                            
                                                label = 'Paid Amount\n'+str(found_fee[2])+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3]) +'\n'+'Bill No:'+str(found_fee[5])+'Paid On :\n'+str(found_fee[6])
                                            else:
                                                label='Paid Amount\n: '+str(found_fee[2])+'\nBill No:'+str(found_fee[5]) +'\nPaid On:'+str(found_fee[6])
                                            sheet1.write(row,month_dict_ids[fees2], label,paid_fee)
                                            col_month = col_month + 1
                                            col_fee=col_fee+1
                                        else:
                                            if f.developer_mode:
                                                label = 'Fee Amount:\n '+str(found_fee[2])+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                            else:
                                                label='Fee Amount:\n '+str(found_fee[2])
                                            sheet1.write(row,month_dict_ids[fees2], label,unpaid_fee)
                                            col_month = col_month + 1
                                            col_fee=col_fee+1
                                       
                                         
                                            
                                    else:
                                        if found_fee[4]=='fee_paid':
                                            if f.developer_mode:
                                                label = 'Paid Amount:\n'+str(found_fee[2])+"\nmonth_id:"+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])+'\nBill No:'+str(found_fee[5]) +'\nPaid On:'+str(found_fee[6])
                                            else:
                                                label='Paid Amount:\n '+str(found_fee[2])+'\nBill No:'+str(found_fee[5]) +'\nPaid On :'+str(found_fee[6])
                                            sheet1.write(row,annual_dict_ids[fees2], label,student_white_rows)
                                        else:
                                            if f.developer_mode:
                                                label = 'Fee Amount:\n '+str(found_fee[2])+"\nmonth_id:"+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])+'\nBill No:'+str(found_fee[5]) +'\nPaid On:'+str(found_fee[6])
                                            else:
                                                label='Fee Amount:\n '+str(found_fee[2])
                                            sheet1.write(row,annual_dict_ids[fees2], label,student_white_rows)
                                            
                                        
                                  # if found_fee[3] !='02':
                                   #  sheet1.write(row,annual_dict_ids[fees2[0]], label,student_rows)
                                                 
                                         
 
                                    #    print("found fee",found_fee ,"\nsearch on ______generic id____",fees2,"\nthis_student.......",this_student[0],"\nmonth",month2)
                                    #
                                     #   label = str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                      #  print "label:",label
                                       # sheet1.write(row,col_fee, label,student_rows)
                                        col_fee = col_fee + 1
    
                                     
                                
                        row = row +1
                         
                    
        print "generating exel"
         
        path = os.path.join(os.path.expanduser('~'),'file.xls')
        book.save(path)

        
    def print_defaulter_detailed(self, cr, uid, ids, data):
        result = []
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee_annaul_defaulter_list_name',
            'datas': datas,
        }
        
        # New way of reporting
#     def _convert_to_report(self, cr, uid, data, context):
#         result = {}
# 
#         ip = netifaces.ifaddresses('wlp2s0')[2][0]['addr']
#         file_name = 'warning_letter.pdf'
#         file_path = '/var/www/html/reports/' + file_name
#         print data
#         print context
#         self.pool = pooler.get_pool(cr.dbname)
#         self.cr = cr
#         self.uid = uid
#         records = self.pool.get('cms.exam.retotalling').browse(cr, uid, [data['id']], context)
#         for f in records:
#             if f.name.id:
#                 obj = self.pool.get('cms.entryregis').browse(cr, uid, f.name.id)
#                 name = obj.name
#                 print "name", name
#                  
#                 father = obj.father_name
#                 print "father name", father 
#          
#         doc = SimpleDocTemplate(str(file_path),pagesize=letter,
#                                 rightMargin=72,leftMargin=72,
#                                 topMargin=72,bottomMargin=18)
#         Story=[]
#         #logo = "Some_logo.png"
#           
#         formatted_time = time.ctime()
# #        full_name = "Laltain Khan"
#         address_parts = ["Phase 7, Hayatabad, Peshawar, Pakistan"]
#           
#         #im = Image(logo, 2*inch, 2*inch)
#         #Story.append(im)
#           
#         styles=getSampleStyleSheet()
#         styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
#         ptext = '<font size=12>%s</font>' % formatted_time
#           
#         Story.append(Paragraph(ptext, styles["Normal"]))
#         Story.append(Spacer(1, 12))
#           
#         # Create return address
#         ptext = '<font size=12>%s</font>' % father
#         Story.append(Paragraph(ptext, styles["Normal"]))       
#         for part in address_parts:
#             ptext = '<font size=12>%s</font>' % part.strip()
#             Story.append(Paragraph(ptext, styles["Normal"]))   
#           
#         Story.append(Spacer(1, 12))
#         ptext = '<font size=12>Dear %s:</font>' % father.split()[0].strip()
#         Story.append(Paragraph(ptext, styles["Normal"]))
#         Story.append(Spacer(1, 12))
#           
#         ptext = '<font size=12>This letter has been written to notify you that %s was caught during the midterm exam using Unfair Means, His paper has been cancelled and has been fined Rupees 1000, This letter is writing to warn you that If he is caught again using Unfair Means, we will hold him very thightly and let Imran Wazir sahab fuck him in his skinny Ass.</font>' % (name)
#          
#         Story.append(Paragraph(ptext, styles["Justify"]))
#         Story.append(Spacer(1, 12))
#           
#         ptext = '<font size=12>Thank you very much and we look forward to Hear from you.</font>'
#         Story.append(Paragraph(ptext, styles["Justify"]))
#         Story.append(Spacer(1, 12))
#         ptext = '<font size=12>Sincerely,</font>'
#         Story.append(Paragraph(ptext, styles["Normal"]))
#         Story.append(Spacer(1, 48))
#         ptext = '<font size=12>IM|Sciences</font>'
#         Story.append(Paragraph(ptext, styles["Normal"]))
#         Story.append(Spacer(1, 12))
#         doc.build(Story)
#           
# #         if sys.platform == 'linux2':
# #             subprocess.call(["xdg-open", file])
# #         else:
# #             os.startfile(file)
#  
#         filename = urllib.quote(file_name)
#         url = 'http://'+ ip + '/reports/'+str(filename)       
#          
#         return {
#         'type': 'ir.actions.act_url',
#         'url':url,
#         'target': 'new'
#         }

                
fee_defaulters()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: