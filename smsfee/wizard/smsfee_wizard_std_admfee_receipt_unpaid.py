from openerp.osv import fields, osv
import datetime

class class_std_admfee_receipts_unpaid(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        class_id=''
        for i in self.pool.get('student.admission.register').browse(cr,uid,[std_id]):
            class_id = i.student_class.id
        return class_id
    
    _name = "class.std.admfee.receipts.unpaid"
    _description = "admits student in a selected class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'due_date': fields.date('Due Date'),
              
               }
    _defaults = {'class_id':_get_class}
    
#     def create_unpaid_challans(self, cr, uid ,class_id,std_id):
#         rec = self.pool.get('student.admission.register').browse(cr,uid,std_id)
#         stu_cls_id = rec.student_class.id
#         stu_name = rec.name  
#         stu_id =  self.pool.get('sms.student').search(cr,uid,[('name','=',stu_name),('admitted_to_class','=',stu_cls_id),
#                                                               ('father_name','=',rec.father_name)
#                                                               ])
#         
#         if stu_id:
#             student_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',stu_id[0]),('name','=',stu_cls_id),('state','=','Current')])
#             
#             fee_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',stu_id[0]),('state','=','fee_unpaid')])
#             check_existing_receipt = self.pool.get('smsfee.receiptbook').search(cr ,uid , [('student_id','=',stu_id[0]),
#                                                                                            ('state','=','fee_calculated'),
#                                                                                            ('receipt_date','=',datetime.date.today())
#                                                                                            ])
#             if not check_existing_receipt:
#                 if fee_ids:
#                     receipt_id = self.pool.get('smsfee.receiptbook').create(cr ,uid , {'student_id':stu_id[0],
#                                                                                        'state':'fee_calculated',
#                                                                                        'receipt_date':datetime.date.today()})
#                     std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr,uid,fee_ids)
#                     if receipt_id:
#                         for unpaidfee in std_unpaid_fees:
#                             feelinesdict = {
#                              'fee_type': unpaidfee.fee_type.id,
#                             'student_fee_id': unpaidfee.id,
#                             'fee_month': unpaidfee.fee_month.id,
#                             'receipt_book_id': receipt_id,
#                             'fee_amount':unpaidfee.fee_amount, 
#                             'late_fee':0,
#                             'total':unpaidfee.fee_amount}
#                             create_recbook_lines = self.pool.get('smsfee.receiptbook.lines').create(cr, uid,feelinesdict)
#         return True                    
    
    def print_fee_report(self, cr, uid, ids, data):
       
        result = []
        thisform = self.read(cr, uid, ids)[0]
        #create_challans = self.create_unpaid_challans(cr, uid, ids[0],data['active_id'])
        report = 'smsfee_print_one_student_per_page'
 
        datas = {
             'ids': [],
             'active_ids': data['active_id'],
             'model': 'student.admission.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
        }
                
class_std_admfee_receipts_unpaid()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: