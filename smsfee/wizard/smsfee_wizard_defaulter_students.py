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

class fee_defaulters(osv.osv_memory):
    """
    This wizard was initially developed for printing defaulter students list only, now we are using this for fee analysis purpose, other reports 
    are also added to this, later on its name will be change in .py and xml file
    --last updated: 23 oct 17 by Shahid
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
              'report_type': fields.selection([('summary','Print Summary (Donot show monthly Details'),('detailed','Detailed Report')],'Options'),
              'category':fields.selection([('Academics','Academics'),('Transport','Transport'),('All','All Fee Categories')],'Fee Category'),
              'order_by':fields.selection([('sms_student.name','Student Name'),('sms_student.registration_no','Registration No'),('sms_student.state','Admission Status')],'Order By'),
              'show_phone_no':fields.boolean('Display Contact No')
               }
    _defaults = {
                 'session':_get_active_session,
                 'category':'Academics',
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
        result = []
       
        book=xlwt.Workbook()
        
        header_top =  xlwt.Style.easyxf('font: bold 0, color black,  height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_green;'
                             )
                
        header_feetypes = xlwt.Style.easyxf('font: bold 0, color black, , height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_green;'
                             )
        header_months = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal center, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  light_green;'
                             )
        
        student_rows = xlwt.Style.easyxf('font: bold 0, color black, height 250;'
                             'align: vertical center, horizontal left, wrap on;'
                             'borders: left thin, right thin, bottom thick;'
                             'pattern: pattern solid, fore_colour  white;'
                             )
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
                    sheet1=book.add_sheet(str(class_ctr)+" "+str(this_class.name),cell_overwrite_ok=True)
                    title = this_class.name
                    class_ctr = class_ctr + 1
                    _col = (sheet1.col(1)).width = 200 * 20
                    _col = (sheet1.col(2)).width = 300 * 15
                    
                    #Find all fee types of this class and arrange in one reow of excel
                    sqlfees = """ SELECT smsfee_feetypes.id,smsfee_feetypes.name,
                                CASE
                                  WHEN (subtype != 'Monthly_Fee') THEN '01'
                                  WHEN (subtype = 'Monthly_Fee') THEN '02'
                                  ELSE '00'
                                 END AS sequence_no
                                from smsfee_feetypes
                                where  smsfee_feetypes.category = '"""+str(f.category)+ """'
                                ORDER BY smsfee_feetypes.name,sequence_no """

                    cr.execute(sqlfees)
                    feerec = cr.fetchall()
                    col_fee = 4# this is the column no in sheet for fee header
                    result1 = []
                    for fees in feerec:
                        result1.append(fees[0])
                        #check if this is monthly fee
                        if fees[2] =='02':
                            sql3 = """SELECT id,name from sms_session_months where session_id  = """+str(this_class.session_id.id)+"""order by name """
                            cr.execute(sql3)
                            months = cr.fetchall()
                            result2 = []
                            for this_month in months:
                                ft_name = str(fees[1])+"\n"+str(this_month[1])+"\nmonth_id:"+str(this_month[0])+"\nfee_id:"+str(fees[0])
                                sheet1.write_merge(r1=0, c1=0, r2=2, c2=11)
                                _col = (sheet1.col(col_fee)).height = 400 * 20
                                _col = (sheet1.col(col_fee)).width = 400 * 20
                                sheet1.write(0,3, title,header_feetypes )
                                sheet1.write(3,col_fee,ft_name,header_feetypes )
                                result2.append(this_month[0])
                                col_fee = col_fee +1
                                 #popluate dict1 for mnthly fees
                        else:
                            sheet1.write_merge(r1=0, c1=0, r2=2, c2=11)
                            _col = (sheet1.col(col_fee)).height = 200 * 20
                            _col = (sheet1.col(col_fee)).width = 300 * 20
                            sheet1.write(0,3, title,header_feetypes )
                            ft_name = str(fees[1])+"\nfee_id:"+str(fees[0])
                            sheet1.write(3,col_fee,ft_name,header_feetypes )
                            #popluate dict1 for non mnthly fees
                            col_fee = col_fee +1
                    
                    #get students for selected class
                    print "total "+str(len(result1))+ " records found in list1"
                    sql4 = """ SELECT id,registration_no, name,state from sms_student where current_class= """+str(this_class.id)+ """ 
                               order by registration_no,name """
                    cr.execute(sql4)
                    students = cr.fetchall()
                    row = 5
                    #set column again to start iele left most 
                    
                    for this_student in students:
                        _col = (sheet1.col(1)).width = 200 * 20
                        sheet1.write(row,1, this_student[1],student_rows )
                        sheet1.write(row,2, this_student[2],student_rows )
                        #now loop via the fees dictionaru for this student
                        col_fee = 4
                        for fees2 in result1:
                            for month2 in result2:
                                sql5 = """select id,fee_month,fee_amount,generic_fee_type
                                          from smsfee_studentfee where student_id =  """+str(this_student[0])+"""
                                          and generic_fee_type= """+str(fees2)+""" and fee_month="""+str(month2)
                              
                                cr.execute(sql5)
                                stdfee = cr.fetchall()
                               
                                for found_fee in stdfee:
                                    label = str(found_fee[2])+"\nmonth_id:"+str(month2)+"\nfee_id:"+str(fees2)+"\nfee_id_genric:"+str(found_fee[3])
                                    print "label:",label
                                    sheet1.write(row,col_fee, label,student_rows)
                                    col_fee = col_fee + 1
                               
                        row = row +1

                   
        print "generating exel"
        
        path = os.path.join(os.path.expanduser('~'),'file.xls')
        print "path",path
        print "book",book
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