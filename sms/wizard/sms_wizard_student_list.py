from openerp.osv import fields, osv
import datetime
import xlwt
import socket
import fcntl
import struct
from struct import pack, unpack

class sms_student_list(osv.osv_memory):

    _name = "sms.studentlist"
    _description = "will print student list"
    _columns = {
              'acad_cal':fields.many2one('sms.academiccalendar','Academic Calendar',domain = [('state','=','Active')] ),
              'list_type': fields.selection([('class_list','Class List'),('contact_list','Contact list'),('check_admissions','Check Admissions')], 'List Type', required = True),
              'start_date': fields.date('Start Date'),
              'end_date':fields.date('End Ddate'),
              'export_to_excel':fields.boolean('Save As MS Excel File')
             }
    _defaults = {
           }

    def print_list(self, cr, uid, ids, data):
        result = []
        thisform = self.browse(cr, uid, ids)[0]
        listtype = thisform['list_type']
        if listtype == 'check_admissions':
            report = 'sms.std_admission_statistics.name'
        
        elif listtype == 'class_list':
            report = 'ssms.class.list.name'
        else:
            student_cal_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',thisform['acad_cal'].id)])
            if not student_cal_ids:
                raise osv.except_osv(('Student Not Found'),('No Student exists in selected class.'))
            student_rows =  self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_cal_ids)
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