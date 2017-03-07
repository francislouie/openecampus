from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_singlestudent_fee_receipt_openchallans(osv.osv_memory):
    
    def _get_challan(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        challan_id =  obj.id
        return challan_id
    
    _name = "class.singlestudent_fee_receipt_openchallans"
    _description = "Single Student's Unpaid Fee Receipt"
    _columns = {
              'challan_id': fields.many2one('smsfee.receiptbook', 'Challan', domain="[('state','=','fee_calculated')]", help="Challan"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Fine After Due Date'),
               }
    _defaults = {'challan_id':_get_challan}
    
    def print_singlestudent_fee_report_openchallans(self, cr, uid, ids, data):
        report = 'smsfee.open.challans'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.receiptbook',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
class_singlestudent_fee_receipt_openchallans()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: