from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class class_fee_receipts_unpaid(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.fee.receipts.unpaid"
    _description = "admits student in a selected class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'due_date': fields.date('Due Date'),
              
               }
    _defaults = {'class_id':_get_class}
    
    def create_unpaid_challans(self, cr, uid, class_id):
        _logger.warning("Deprecated, usle c............................................................................")
        student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',class_id[0]),('state','=','Current')])
        if student_ids:
            recstudent = self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_ids)
            for student in recstudent:
                self.pool.get('smsfee.receiptbook').check_fee_challans_issued(cr, uid, class_id[0], student.std_id.id)
        return True
    
    def print_fee_report(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        self.create_unpaid_challans(cr, uid, thisform['class_id'])
        report = 'smsfee_unpaidfee_receipt_name'        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
        }
                
class_fee_receipts_unpaid()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: