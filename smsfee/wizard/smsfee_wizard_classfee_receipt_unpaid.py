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
        print "&&&&&&&&&&&"
        _logger.warning("Deprecated, usle c............................................................................")
        student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',class_id[0]),('state','=','Current')])
        if student_ids:
            recstudent = self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_ids)
            for student in recstudent:
                 
                fee_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',student.std_id.id),('state','=','fee_unpaid')])
                if fee_ids:
                    total_paybles = 0
                    receipt_id = self.pool.get('smsfee.receiptbook').create(cr ,uid , {'student_id':student.std_id.id,'student_class_id':class_id[0],'state':'fee_calculated','receipt_date':datetime.date.today()})
                    std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr,uid,fee_ids)
                    if receipt_id:
                        for unpaidfee in std_unpaid_fees:
                            total_paybles = total_paybles + unpaidfee.fee_amount
                            feelinesdict = {
                            'fee_type': unpaidfee.fee_type.id,
                            'student_fee_id': unpaidfee.id,
                            'fee_month': unpaidfee.fee_month.id,
                            'receipt_book_id': receipt_id,
                            'fee_amount':unpaidfee.fee_amount,
                            'late_fee':0,
                            'total':unpaidfee.fee_amount}
                            create_recbook_lines = self.pool.get('smsfee.receiptbook.lines').create(cr, uid,feelinesdict)
        return True
    

    
    def print_fee_report(self, cr, uid, ids, data):
       
        print "))))((((((((((((((((((((((((((((((()()))))))))))))"
       
        result = []
        thisform = self.read(cr, uid, ids)[0]
        print "**********",_logger.warning('class 1111111111111111111111111111111.')
        create_challans = self.create_unpaid_challans(cr, uid, thisform['class_id'])
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