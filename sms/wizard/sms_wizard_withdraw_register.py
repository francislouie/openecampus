from openerp.osv import fields, osv
import datetime

class sms_withdraw_register(osv.osv_memory):
    """Use this wizard to withdraw student from the school, cases may be student (struck_off,admission cancel,slc,deceased)"""
     
    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    _name = "sms.withdraw.register"
    _description = "withdraws student from the school"
    _columns = {
               #'session_id': fields.many2one('sms.session', 'Session', help="Select a session",required = True),
               'session_ids':fields.many2many('sms.session', 'withdraw_register_session_rel', 'sms_withdraw_register_id', 'session_id', 'Session'),
               'order_by': fields.selection([('registration_no','Registration No'),('name','Student Name'),('admitted_on','Date of Admission'),('date_withdraw','Date of withdraw'),('current_class','Class')],'Order By', required = True),
             }
    _defaults = {
           }
  
    def print_list(self, cr, uid, ids, data):
        result = []
        
            
        
        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.studentlist',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'sms.withdraw.register.name',
            'datas': datas,
        }
    
sms_withdraw_register()

