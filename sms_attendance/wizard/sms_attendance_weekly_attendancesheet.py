from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_print_weekly_attendance_sheet(osv.osv_memory):
    
    _name = "class.print_weekly_attendance_sheet"
    _description = "Used To Print Weekly Attendance Summary Sheet"
    
    _columns = {
                'session_id': fields.many2one('sms.session', 'Session', domain="[('state','=','Active')]", required=True, help="Class"),
                'week': fields.many2one('sms.calander.week','Calender Week', required=True),
               }
    _defaults = {} 
    
    def print_weekly_attendance_list(self, cr, uid, ids, context=None):
        report = 'smsattendance.weekly.attendance.sheet'
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'class.print_weekly_attendance_sheet',
            'form': self.read(cr, uid, ids)[0]
            }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas
            }
       
class_print_weekly_attendance_sheet()
