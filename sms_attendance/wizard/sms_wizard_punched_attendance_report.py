from openerp.osv import fields, osv
import datetime

class class_punched_attendance(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
       # obj = self.browse(cr, uid, ids['active_id'])
        #std_id =  obj.id
        std_id = None
        return std_id
    
    _name = "class.punched.attendance"
    _description = "shows punched attendance of selected class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]", help="Class"),
              'today': fields.date('Date'),
              'helptext':fields.text('helptext')
               }
    _defaults = {
                 'class_id':_get_class,
                 'helptext':'Select class name to show attendance detail of  selected class.'
           }
    
    def print_view_attendance_report(self, cr, uid, ids, data):
        result = []
        thisform = self.read(cr, uid, ids)[0]
        report = 'report_disply_attendance'        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.class.attendance',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
        }
        #return None
                
class_punched_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: