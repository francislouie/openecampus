from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_print_blank_attendance_sheet(osv.osv_memory):
    
    _name = "class.print_blank_attendance_sheet"
    _description = "Used To Print Blank Attendance Sheet"
    
    _columns = {
              'class_id': fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]", required=True, help="Class"),
               }
    _defaults = {} 
    
    def print_blank_attendance_list(self, cr, uid, ids, context=None):
        report = 'smsattendance.blank.attendance.sheet'
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
       
class_print_blank_attendance_sheet()
