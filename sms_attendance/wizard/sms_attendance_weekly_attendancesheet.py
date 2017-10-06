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
        datas = self.read(cr, uid, ids)[0]
        week = datas['week']
        session = datas['session_id']

        week_id = week[0]
        session_id = session[0]
        
        return {
            'type': 'json',
            'datas': datas,
            'week_id': week_id,
            'session_id': session_id
            }
       
class_print_weekly_attendance_sheet()
