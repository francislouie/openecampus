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
        vehcile_filter = self.datas['form']['vehcile_filter']
        route_filter = self.datas['form']['route_filter']

        if class_filter:
            class_id = self.datas['form']['class_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_academiccalendar
                            ON sms_student.current_class = sms_academiccalendar.id
                            AND current_class = """+ str(class_id) +""" 
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()

        elif route_filter:
            route_id = self.datas['form']['route_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_transport_route_vehcile_rel
                            ON sms_transport_registrations.current_vehcile = sms_transport_route_vehcile_rel.sms_transport_route_id
                            AND sms_transport_route_vehcile_rel.sms_transport_vehcile_id = """+ str(route_id) +"""
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()

        elif vehcile_filter:
            vehcile_id = self.datas['form']['vehcile_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_transport_route_vehcile_rel
                            ON sms_transport_registrations.current_vehcile = sms_transport_route_vehcile_rel.sms_transport_route_id
                            AND sms_transport_route_vehcile_rel.sms_transport_route_id = """+ str(vehcile_id) +"""
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()
            
        elif class_filter and vehcile_filter:
            class_id = self.datas['form']['class_id'][0]
            vehcile_id = self.datas['form']['vehcile_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_academiccalendar
                            ON sms_student.current_class = sms_academiccalendar.id
                            AND current_class = """+ str(class_id) +""" 
                            AND vehcile_reg_students_id = """+ str(vehcile_id) +"""
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()
            
        elif class_filter and route_filter :
            class_id = self.datas['form']['class_id'][0]
            route_id = self.datas['form']['route_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_academiccalendar
                            ON sms_student.current_class = sms_academiccalendar.id
                            INNER JOIN sms_transport_route_vehcile_rel
                            ON sms_transport_registrations.current_vehcile = sms_transport_route_vehcile_rel.sms_transport_route_id
                            AND current_class = """+ str(class_id) +""" 
                            AND sms_transport_route_vehcile_rel.sms_transport_vehcile_id = """+ str(route_id) +"""
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()
            
        elif route_filter and vehcile_filter:
            route_id = self.datas['form']['route_id'][0]
            vehcile_id = self.datas['form']['vehcile_id'][0]
            student_sql = """SELECT sms_transport_registrations.student_id FROM sms_transport_registrations 
                            INNER JOIN sms_student
                            ON sms_transport_registrations.student_id = sms_student.id
                            INNER JOIN sms_transport_route_vehcile_rel
                            ON sms_transport_registrations.current_vehcile = sms_transport_route_vehcile_rel.sms_transport_route_id
                            AND sms_transport_route_vehcile_rel.sms_transport_vehcile_id = """+ str(route_id) +"""
                            AND sms_transport_route_vehcile_rel.sms_transport_route_id = """+ str(vehcile_id) +"""
                            ORDER BY sms_transport_registrations.student_id"""
            self.cr.execute(student_sql)
            student_records = self.cr.fetchall()
                            
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
        return result  
              
report_sxw.report_sxw('report.smstransport_registered_entries', 
                      'sms.transport.registrations', 
                      'addons/smstransport/report/smstransport_registered_students.rml',
                      parser = transport_registered_students, header=None)
