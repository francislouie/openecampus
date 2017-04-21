from openerp.osv import fields, osv
import datetime

class admit_student(osv.osv_memory):

    _name = "admit.student"
    _description = "Help student admission"
    _columns = {
              'help ': fields.many2one('sms.student', 'Student', help="Student to be admitted", readonly = True),
               }
admit_student()
   
   
