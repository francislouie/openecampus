from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class open_challns_wizardlines(osv.osv_memory):
    _name = 'open.challns.wizardlines'
    _rec_name = 'challno'
    _columns = {
        'challno': fields.char('Bill No'),
        'amount': fields.float('Amount'),
        'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category'),
        'status_after_print':fields.selection([('Open','Open'),('Cancel','Will be Cancel')],'Fee Bill Future'),
        'wizard_id': fields.many2one('class.singlestudent_fee_receipt_openchallans', 'Parent'),
    }


class class_singlestudent_unpaidfee_receipt(osv.osv_memory):
    
    """this wizard is used to print single student fee challan both for transport and cademics, from 14 may 2017 """
    
    def _get_student(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.singlestudent_unpaidfee_receipt"
    _description = "Single Student's Unpaid Fee Receipt"
    _columns = {
              'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category'),
              'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Fine After Due Date'),
              'exiting_challan_ids': fields.one2many('open.challns.wizardlines','wizard_id', 'Existing Bills'),
               }
    _defaults = {'student_id':_get_student,'category':'Academics','amount_after_due_date':200}
    
    def create_unpaid_challans(self, cr, uid, student_id,category):
        _logger.warning("Deprecated ............................................................................")
        student_id = self.pool.get('sms.student').search(cr,uid,[('id','=',student_id[0])])
        class_id = self.pool.get('sms.student').browse(cr,uid,student_id)[0].current_class.id
        self.pool.get('smsfee.receiptbook').check_fee_challans_issued(cr, uid, class_id, student_id[0],category)
        return True

    def print_singlestudent_unpaidfee_report(self, cr, uid, ids, data):

        thisform = self.read(cr, uid, ids)[0]
        
        if thisform['category'] == 'Academics':
            self.create_unpaid_challans(cr, uid, thisform['student_id'],'Academics')
            report = 'smsfee_stu_unpaidfee_receipt_name'
        elif thisform['category'] == 'Transport':
            self.create_unpaid_challans(cr, uid, thisform['student_id'],'Transport')
            report = 'smstransport_stu_unpaidtransportfee_receipt'
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
        
class_singlestudent_unpaidfee_receipt()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: