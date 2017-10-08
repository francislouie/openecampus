from openerp.osv import fields, osv
from datetime import date, timedelta, datetime
import logging
import xlwt
import socket
import fcntl
import struct
import urllib

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
        
        book=xlwt.Workbook()
        sheet = book.add_sheet('Sheet',cell_overwrite_ok=True)
        sheet.portrait = False
        
        #location="/var/www/excel/"  
        location="/var/www/excel2/"
        filename= """First_Sheet.xls"""
        
        #********************************************************************************88
        
        heading = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;' 'font: name Calibri, bold on, height 280, color_index 0X36;' 'align: horiz center, wrap 1;''borders: left thin, right thin, top thin, bottom thin')
        sub_heading = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;' 'font: name Calibri, bold on, height 230;' 'align: horiz left, wrap 1;''borders: left thin, right thin, top thin, bottom thin')
        heading2 = xlwt.easyxf('pattern: pattern solid, fore_colour lavender;' 'font: bold on, height 230;''align: horiz center, wrap 1;''borders:  left thin, right thin, top thin, bottom thin')
        style2 = xlwt.easyxf('align: horiz center, wrap 1;''borders:  left thin, right thin, top thin, bottom thin')
        style3 = xlwt.easyxf('align: horiz center, wrap 1;''borders:   left thin, right thin, top thin, bottom thin')
        text_style2 = xlwt.easyxf('align: horiz left, wrap 1;''borders:  left thin, right thin, top thin, bottom thin')
        text_style3 = xlwt.easyxf('align: horiz left, wrap 1;''borders:   left thin, right thin, top thin, bottom thin')
        

        _col = sheet.col(1)
        _col.width = 300 * 20
        _col = sheet.col(2)
        _col.width = 300 * 20
        _col = sheet.col(5)
        _col.width = 300 * 20
        _col = sheet.col(6)
        _col.width = 300 * 20        
        _col = sheet.col(9)
        _col.width = 300 * 20
        _col = sheet.col(10)
        _col.width = 300 * 20

        _col = sheet.col(0)
        _col.width = 80 * 20
        _col = sheet.col(3)
        _col.width = 80 * 20
        _col = sheet.col(4)
        _col.width = 100 * 20        
        _col = sheet.col(8)
        _col.width = 100 * 20
        
        
        sheet.write_merge(r1=0, c1=0, r2=1, c2=15)                           
        sheet.write(0, 0, 'Weekly Attendance Report',heading)
        
        sheet.write_merge(r1=2, c1=0, r2=2, c2=15)
        sheet.write(2, 0, session[1],sub_heading)                          
        
        
        sheet.write(4, 0, 'Class',heading2)
        sheet.write(4, 1, 'Section',heading2)

        list_of_dates = self.get_week_dates(cr, uid, ids, week_id)
        col = 2
        for d in list_of_dates:
            sheet.write_merge(r1=4, c1=col, r2=4, c2=col+3)
            sheet.write(4, col, d.strftime("%A"), heading2)
            sheet.write_merge(r1=5, c1=col, r2=5, c2=col+3)
            sheet.write(5, col, d.strftime("%d-%m-%Y"), heading2)
            sheet.write(6, col, "Total", heading2)
            sheet.write(6, col+1, "Present", heading2)
            sheet.write(6, col+2, "Absent", heading2)
            sheet.write(6, col+3, "Leave", heading2)
            col = col + 4

        row = 7
        for c in attendances:
            sheet.write(row, 0, c['class'], text_style2)
            sheet.write(row, 1, c['section'], text_style2)
            col = 2
            for d in c['days']:
                sheet.write(row, col, d['total'], style2)
                sheet.write(row, col+1, d['present'], style2)
                sheet.write(row, col+2, d['absent'], style2)
                sheet.write(row, col+3, d['leave'], style2)
                col = col + 4
            row = row + 1

        col = 2
        
        for d in len(list_of_dates)*4:
            sheet.write(row, col, xlwt.Formula("SUM(R[7]C:R[])")) # can't figure out sum formula

        #*************************************************************************************
        # strs=str(location)+str(filename)
        # book.save(strs)
                
        # company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('name','=','Institute of Management Sciences (IM | Sciences), Peshawar')])
        # company_obj = pooler.get_pool(cr.dbname).get('res.company').browse(cr, uid, company_id)
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ip = socket.inet_ntoa(fcntl.ioctl(
        #                                 s.fileno(),
        #                                 0x8915,  # SIOCGIFADDR
        #                                 struct.pack('256s', str(company_obj[0].network_connection_interface)[:15])
        #                             )[20:24])
        # filename = urllib.quote(filename)
        #url = 'http://'+ip+'/excel2/'+str(filename)
        # url = 'http://localhost:8007/excel2/'+str(filename)
        # return {
        # 'type': 'ir.actions.act_url',
        # 'url':url,
        # 'target': 'new'
        # } 
        return {
        'type': 'json', 
        'attendances': attendances
        }

    def get_week_dates(self, cr, uid, ids, week_id, context=None):
        week_obj = self.pool.get('sms.calander.week').browse(cr, uid, week_id)

        start_date = datetime.strptime(week_obj.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(week_obj.end_date, '%Y-%m-%d')

        delta = end_date - start_date
        list_of_dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
        list_of_dates = [d for d in list_of_dates if d.strftime("%A") != 'Sunday']
        return list_of_dates

    def get_weekly_attendance_data(self, cr, uid, ids, week_id, session_id, context=None):
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr, uid, [('session_id','=',session_id)])
        academiccalendar_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, academiccalendar_ids)

        list_of_dates = self.get_week_dates(cr, uid, ids, week_id)
        
        attendances = []
        for i, k in enumerate(academiccalendar_obj):
            my_dict = {}
            
            my_dict['class'] = k.class_id.name
            my_dict['section'] = k.section_id.name

            days = []
            for d in list_of_dates:
                day = {}
                day['date'] = str(d)
                day['day'] = weekday
                day.update(k.get_class_attendance(k.id, d))
                days.append(day)
            
            my_dict['days'] = days
            attendances.append(my_dict)

        return attendances
       
class_print_weekly_attendance_sheet()
