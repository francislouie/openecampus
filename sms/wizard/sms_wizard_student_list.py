from openerp.osv import fields, osv

class sms_student_list(osv.osv_memory):

    _name = "sms.studentlist"
    _description = "Used to Print Students List in Multiple Formats"
    _columns = {
              'acad_cal':fields.many2one('sms.academiccalendar','Academic Calendar', domain=[('state','=','Active')]),
              'list_type': fields.selection([('class_list','1.Class List'),
                                             ('contact_list','2.Contact list'),
                                             ('check_admissions','3.Check Admissions Statistics'),
                                             ('biodata','4. Student Biodata'),
                                             ('security_cards','5. Students Security Cards'),
                                             ('withdrawn_students','6. Withdrawn Students'),
                                             ('students_strength','7. Student Strength Report')], 'List Type', required=True),
              'start_date': fields.date('Start Date'),
              'student_ids':fields.many2many('sms.student','sms_student_cards_rel', 'student_id', 'card_id', 'Students'),
              'end_date':fields.date('End Date'),
              'card_display_message':fields.char('Display Text'),
              'export_to_excel':fields.boolean('Save As MS Excel File'),
              'class_form': fields.boolean('Class View'),
             }
    _defaults = { 'list_type': 'check_admissions',
                 'class_form': False
                 
           }

    def print_list(self, cr, uid, ids, data):
        thisform = self.browse(cr, uid, ids)[0]
        listtype = thisform['list_type']
        if listtype == 'check_admissions':
            report = 'sms.std_admission_statistics.name'
        elif listtype == 'class_list':
            report = 'sms.class.list.name'
        elif listtype == 'security_cards':
            report = 'sms_students_securuty_cards_name'
        elif listtype == 'biodata':
            report = 'sms.students.biodata'
        elif listtype == 'withdrawn_students':
            report = 'sms.withdrawn.student.details'
        elif listtype == 'students_strength':
            report = 'sms.student.strength.report'
        else:
            student_cal_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',thisform['acad_cal'].id)])
            if not student_cal_ids:
                raise osv.except_osv(('Student Not Found'),('No Student exists in selected class.'))
            self.pool.get('sms.academiccalendar.student').browse(cr, uid, student_cal_ids)
            report = 'sms.studentslist.name'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.studentlist',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
sms_student_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: