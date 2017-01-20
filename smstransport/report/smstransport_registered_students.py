import time
from report import report_sxw
 
class transport_registered_students(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
 
        super(transport_registered_students, self).__init__(cr, uid, name, context)
        self.result_temp=[]
        self.localcontext.update({
            'get_today':self.get_today,
            'get_user_name':self.get_user_name,
            'get_registered_students_transport':self.get_registered_students_transport,
         })
        self.context = context
     
    def get_today(self):
        today = time.strftime('%d-%m-%Y')
        return today 

    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context).name
        return user_name
     
    def get_registered_students_transport(self, data):
        result = []
        class_filter = self.datas['form']['class_filter']
        class_id = self.datas['form']['class_id'][0]
        vehcile_filter = self.datas['form']['vehcile_filter']
        vehcile_id = self.datas['form']['vehcile_id'][0]
        route_filter = self.datas['form']['route_filter']
#        route_id = self.datas['form']['route_id'][0]
        if class_filter and vehcile_filter:
            
            student_sql = """SELECT id FROM sms_student WHERE current_class = """+ str(class_id) +""" 
            AND transport_availed = True
            AND vehcile_reg_students_id = """+ str(vehcile_id) +""""""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()
                
        if class_filter and route_filter:
            student_ids = self.pool.get('sms.student').search(self.cr, self.uid,[('admitted_to_class','=',class_id)])
            student_transportreg_ids = self.pool.get('sms.transport.registrations').search(self.cr, self.uid,[('student_id','in',student_ids)])        
        if route_filter and vehcile_filter:
            student_ids = self.pool.get('sms.student').search(self.cr, self.uid,[])
        if class_filter and vehcile_filter and route_filter:
            student_ids = self.pool.get('sms.student').search(self.cr, self.uid,[])
        
        counter = 0
        for rec in student_records:
            my_dict = {'sno':'','name':'','father_name':'', 'phone':'', 'email':'', 'class':''}
            counter = counter + 1
            student_record = """SELECT name, father_name FROM sms_student WHERE id = """+ str(rec[0]) +""""""
            self.cr.execute(student_record)
            student_record  = self.cr.fetchone()
            my_dict['sno']  = counter
            my_dict['name'] = student_record[0]
            my_dict['father_name']  = student_record[1]
            result.append(my_dict)
        print "",result
        return result  
     
#     def get_vertical_lines_total(self, data):
#         line_dots = []
#         challan = self.pool.get('sms.transportfee.challan.book').browse(self.cr,self.uid,data)
# #         start = len(challan.receiptbook_lines_ids)
#         start = 5
#         if start >=14:
#             dict = {'line-style':'|'}
#             line_dots.append(dict)
#         else:
#             for num in range(start,14):
#                 dict = {'line-style':'|'}
#                 line_dots.append(dict)
#         return line_dots    
         
report_sxw.report_sxw('report.smstransport_registered_entries', 
                      'sms.transport.registrations', 
                      'addons/smstransport/report/smstransport_registered_students.rml',
                      parser = transport_registered_students, header=None)
