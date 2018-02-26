from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_print_total_absent_attendance_sheet(osv.osv_memory):
    
    _name = "class.print_total_absent_attendance_sheet"
    _description = "Used To Print total absent Attendance Summary Sheet"
    
    _columns = {
              'session_id': fields.many2one('sms.session', 'Session', domain="[('state','=','Active')]", required=True, help="Class"),
              'class_id': fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]", required=True, help="Class"),
              'date': fields.date('Date', required=True),
               }
    _defaults = {} 
    
    def print_total_absent_attendance_list(self, cr, uid, ids, context=None):
        report = 'smsattendance.total.absent.attendance.sheet'
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'class.print_total_absent_attendance_sheet',
            'form': self.read(cr, uid, ids)[0]
            }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas
            }
       
class_print_total_absent_attendance_sheet()
