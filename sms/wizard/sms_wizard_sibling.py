from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class sms_studentsibling_wizard(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "sms.studentsibling.wizard"
    _description = "Print student sibling report"
    _columns = {
              'session_id': fields.many2one('sms.session', 'Session', domain="[('state','=','Active')]"),
              "class_id": fields.many2many('sms.academiccalendar', 'sms_std_sms_wizard_rel', 'sms_studentsibling_wizard_id', 'sms_academiccalendar_id','Classes', domain="[('state','=','Active')]"),
              'order_of_report': fields.selection([('name', 'Name'), ('class','Class')],"Order By")
               }
    
    
    _defaults = {
                 }
    
    def print_list(self, cr, uid, ids, data):
        report = 'sms.student.sibling.name'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'student.admission.register',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
            
sms_studentsibling_wizard()
