from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_print_filled_attendance_sheet(osv.osv_memory):
    
    _name = "class.print_filled_attendance_sheet"
    _description = "Used To Print Blank Attendance Sheet"
    
    _columns = {
                'class_id': fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]", help="Class"),
                'date_from': fields.date('Month'),
#                 'date_to':fields.date('Date To'),
               }
    _defaults = {} 
    
    def print_filled_attendance_list(self, cr, uid, ids, context=None):
        report = 'smsattendance.filled.attendance.sheet'
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.academiccalendar',
            'form': self.read(cr, uid, ids)[0]
            }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas
            }
       
class_print_filled_attendance_sheet()
