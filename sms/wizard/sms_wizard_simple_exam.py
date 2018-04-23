from openerp.osv import fields, osv
import datetime

class simple_exam_entry(osv.osv_memory):
    _name = "simple.exam.entry"
    _description = "Timetable Entry"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True),
                'exam_name': fields.char('Exam Name',size=300),
              }
    _defaults = {
                 
           }
     
simple_exam_entry()

