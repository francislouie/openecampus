from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class class_fee_receipts_unpaid_2(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.fee.receipts.unpaid.2"
    _description = "Used To Print Transport Fee Challans"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              "payment_id": fields.many2one('sms.transport.fee.payments', 'Payment', domain="[('state','=','Unpaid')]"),
               }
    _defaults = {'class_id':_get_class}
    
    def create_unpaid_challans(self, cr, uid, class_id):
        _logger.warning("Printing Challan ,------------- ")
        class_student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',class_id[0]),('state','=','Current')])
        if class_student_ids:
            recstudent = self.pool.get('sms.academiccalendar.student').browse(cr,uid,class_student_ids)
            for student in recstudent:
                #-----------Get only those students of this class who are registered in transport ---------------------
                student_id = self.pool.get('sms.student').search(cr,uid,[('transport_availed','=',True),('id','=',student.std_id.id)])
                rec_student   = self.pool.get('sms.student').browse(cr,uid,student_id)
                
                for rec in rec_student:
                    fee_ids = self.pool.get('sms.transport.fee.payments').search(cr,uid,[('student_id','=',rec.id),('state','=','Unpaid')])
                    fee_recs = self.pool.get('sms.transport.fee.payments').browse(cr,uid, fee_ids)
                    #-----------------Check if same record exists in challan book or not, if it does exist then donot create record
                    check_existing_id = self.pool.get('sms.transportfee.challan.book').search(cr,uid,[('student_id','=',rec.id),('state','=','fee_calculated'),('student_class_id','=',class_id[0])])
                    if check_existing_id:
                        return True
                    #------------- Create Transport Challan Records --------------------------
                    receipt_id = self.pool.get('sms.transportfee.challan.book').create(cr ,uid , 
                                               {'student_id':rec.id,
                                                'student_class_id':class_id[0],
                                                'state':'fee_calculated',
                                                'receipt_date':datetime.date.today()})
                    if fee_recs:
                        total_payables = 0
                        for record in fee_recs:
                            #-----------------Check if same record exists in challan book lines or not, if it does exist then donot create record
                            trans_challan_lines = self.pool.get('sms.transport.fee.challan.lines').search(cr, uid,[('student_fee_id','=',record.id),('receipt_book_id','=',receipt_id)])
                            if trans_challan_lines:
                                return True
                            if receipt_id:
                                total_payables = total_payables + record.fee_amount
                                self.pool.get('sms.transportfee.challan.book').write(cr,uid,receipt_id,
                                                                                     {'total_payables':total_payables})                                
                                feelinesdict = {
                                'fee_type': 1,
        #                                'fee_type': unpaidfee.fee_type.id,
                                'student_fee_id': record.id,
                                'fee_month': record.fee_month.id,
                                'receipt_book_id': receipt_id,
                                'fee_amount':record.fee_amount,
                                'late_fee':0,
                                'total':total_payables}
                                self.pool.get('sms.transport.fee.challan.lines').create(cr, uid,feelinesdict)
        return True
    
    def print_fee_report_2(self, cr, uid, ids, data):
       
        result = []
        thisform = self.read(cr, uid, ids)[0]
        print "**********",_logger.warning('Payment Id -----------')
        self.create_unpaid_challans(cr, uid, thisform['class_id'])
        report = 'smstransport_unpaid_receipts_name'        
 
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
                
class_fee_receipts_unpaid_2()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: