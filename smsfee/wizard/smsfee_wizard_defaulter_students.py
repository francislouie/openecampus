from openerp.osv import fields, osv
import datetime

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

class fee_defaulters(osv.osv_memory):

    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
    
    _name = "fee.defaulters"
    _description = "Prints defaulter list"
    _columns = {
              "session": fields.many2one('sms.session', 'Session', help="Select A session , you can also print reprts from previous session."),
              "class_id": fields.many2many('sms.academiccalendar','sms_academiccalendar_class_fee', 'thisobj_id', 'academiccalendar_id','Class', domain="[('session_id','=',session),('fee_defined','=',1)]"),
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