from openerp.osv import fields, osv
from datetime import date, timedelta, datetime
import logging
_logger = logging.getLogger(__name__)

class class_print_weekly_attendance_sheet(osv.osv_memory):
    
    _name = "class.print_weekly_attendance_sheet"
    _description = "Used To Print Weekly Attendance Summary Sheet"
    
    _columns = {
                'session_id': fields.many2one('sms.session', 'Session', domain="[('state','=','Active')]", required=True, help="Class"),
                'week_id': fields.many2one('sms.calander.week','Calender Week', required=True),
               }
    _defaults = {} 
    
    def print_weekly_attendance_list(self, cr, uid, ids, context=None):
        datas = self.read(cr, uid, ids)[0]
        week = datas['week_id']
        session = datas['session_id']

        week_id = week[0]
        session_id = session[0]

        attendances = self.get_weekly_attendance_data(cr, uid, ids, week_id, session_id, context)
        
        return {
            'type': 'json',
            'attendances': attendances,
            }

    def get_weekly_attendance_data(self, cr, uid, ids, week_id, session_id, context=None):
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr, uid, [('session_id','=',session_id)])
        academiccalendar_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, academiccalendar_ids)

        week_obj = self.pool.get('sms.calander.week').browse(cr, uid, week_id)

        start_date = datetime.strptime(week_obj.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(week_obj.end_date, '%Y-%m-%d')

        delta = end_date - start_date
        list_of_dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
        str_list_of_dates = [str(i) for i in list_of_dates]
        
        attendances = []
        for i, k in enumerate(academiccalendar_obj):
            my_dict = {}
            
            my_dict['class'] = k.class_id.name
            my_dict['section'] = k.section_id.name

            days = []
            for d in list_of_dates:
                weekday = d.strftime("%A")
                if (weekday != "Sunday"):
                    day = {}
                    day['date'] = str(d)
                    day['day'] = weekday
                    day.update(k.get_class_attendance(k.id, d))
                    days.append(day)
            
            my_dict['days'] = days
            attendances.append(my_dict)

        return attendances
       
class_print_weekly_attendance_sheet()
