from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_student_transportfee_existing_challans(osv.osv_memory):
    
    def _get_challan(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        challan_id =  obj.id
        return challan_id
    
    _name = "class.student_transportfee_existing_challans"
    _description = "Single Student's Unpaid Fee Receipt"
    _columns = {
              'challan_id': fields.many2one('sms.transportfee.challan.book', 'Challan', domain="[('state','=','fee_calculated')]", help="Challan"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Fine After Due Date'),
               }
    _defaults = {'challan_id':_get_challan}
    
    def print_student_transport_existing_challans(self, cr, uid, ids, data):
        report = 'smstransportfee.open.challans'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.transport.fee.payments',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
class_student_transportfee_existing_challans()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: