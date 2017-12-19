from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_student_fee_collect(osv.osv_memory):
    
    def _get_student(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.student_fee_collect"
    _description = "Student's Fee Collection"
    _columns = {
              'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'challan_id': fields.many2one('smsfee.receiptbook', 'Fee Bill', domain="[('state','=','fee_calculated'),('student_id','=',student_id)]", help="Challan", required=True),
               }
    _defaults = {'student_id':_get_student}

    def action_pay_student_fee(self, cr, uid, ids, context):
        domain = []
        thisform = self.read(cr, uid, ids)[0]        
        domain = [('id','>=',thisform['challan_id'][0])]
                
        result = {
                'type': 'ir.actions.act_window',
                'name': 'Collect Fees',
                'res_model': 'smsfee.receiptbook',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'nodestroy': True,
                'target': 'current',
                'domain': domain,
                }

        return result 
    
class_student_fee_collect()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: