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
              'display_draft_waitapprov':fields.boolean('Display Draft and Waiting'),
             }
    _defaults = { 'list_type': 'students_strength',
                 'class_form': False
                 
           }

    def print_list(self, cr, uid, ids, data):
        sqluser = """ select res_groups.name from res_groups inner join res_groups_users_rel 
               on res_groups.id=res_groups_users_rel.gid where res_groups_users_rel.uid=""" + str(uid)
        cr.execute(sqluser)
        group_name = cr.fetchall()
        Faculty_group = False
        for s in group_name:
            if s[0] == 'Faculty':
                Faculty_group = True


        thisform = self.browse(cr, uid, ids)[0]
        listtype = thisform['list_type']
        if listtype == 'check_admissions':
            if Faculty_group:
                raise osv.except_osv(('Teachers is not authorized'), ('Restriction.'))
            else:
                report = 'sms.std_admission_statistics.name'
        elif listtype == 'class_list':
            if Faculty_group:
                raise osv.except_osv(('Teacher is not authorized'), ('Restriction.'))
            else:
                report = 'sms.class.list.name'
        elif listtype == 'security_cards':
            if Faculty_group:
                raise osv.except_osv(('Teacher is not authorized'), ('Restriction.'))
            else:
                report = 'sms_students_securuty_cards_name'
        elif listtype == 'biodata':
            if Faculty_group:
                raise osv.except_osv(('Teacher is not authorized'), ('Restriction.'))
            else:
                report = 'sms.students.biodata'
        elif listtype == 'withdrawn_students':
            if Faculty_group:
                raise osv.except_osv(('Teacher is not authorized'), ('Restriction.'))
            else:
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