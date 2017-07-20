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
    _defaults = {}

class class_singlestudent_unpaidfee_receipt(osv.osv_memory):
    
    """this wizard is used to print single student fee challan both for transport and cademics, from 14 may 2017 """
    
    def _get_student(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    def _get_unpaid_fee_months(self, cr, uid, ids):
        result = []
        obj = self.browse(cr, uid, ids['active_id'])
        sql = """SELECT DISTINCT tab1.fee_month
                FROM smsfee_studentfee as tab1
                INNER JOIN smsfee_classes_fees_lines as tab2
                ON tab1.fee_type = tab2.id
                INNER JOIN smsfee_feetypes as tab3
                ON tab2.fee_type = tab3.id
                WHERE tab1.student_id= '"""+str(obj.id)+"""' AND state = 'fee_unpaid'
                AND tab3.category = 'Academics'"""
                
        cr.execute(sql)
        unpaidfee_ids = cr.fetchall()
        for rec in unpaidfee_ids:
            if not rec[0]:
                continue
            else:
                result.append(rec[0])
        return result

#     def _get_existing_challans(self, cr, uid, ids):
#         result = []
#         mydict={}
#         obj = self.browse(cr, uid, ids['active_id'])
#         unpaid_challan_ids = self.pool.get('smsfee.receiptbook').search(cr, uid, [('student_id','=',obj.id),('state','=','fee_calculated')])
#         unpaid_challan_objs = self.pool.get('smsfee.receiptbook').browse(cr, uid, unpaid_challan_ids)
#         for unpaidfee_id in unpaid_challan_objs:
#             if unpaidfee_id.challan_cat == obj.category:
#                 printstatus = 'Cancel'
#             else:
#                 printstatus = 'Open'
#             printstatus = '12'
#             mydict['challno'] = unpaidfee_id.counter
#             mydict['amount']=unpaidfee_id.total_paybles,
#             mydict['category']=unpaidfee_id.challan_cat,
#             mydict['status_after_print']=printstatus
#             result.append(mydict)
#         return result
        
    _name = "class.singlestudent_unpaidfee_receipt"
    _description = "Single Student's Unpaid Fee Receipt"
    _columns = {
              'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category'),
              'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Fine After Due Date'),
              'exiting_challan_ids': fields.one2many('open.challns.wizardlines','wizard_id', 'Existing Bills'),
              'fee_receiving_type':fields.selection([('Full','Full'),('Partial','Partial')], 'Challan Type'),
              'unpaidfee_months_id':fields.many2many('sms.session.months', 'singlestd_partialchallan_sessionmonths', 'thisobj_id','months_id', 'Month'),
               }
    _defaults = {'student_id':_get_student,
                 'category':'Academics',
                 'amount_after_due_date':200,
                 'fee_receiving_type': 'Full',
                 'unpaidfee_months_id':_get_unpaid_fee_months,
#                 'exiting_challan_ids':_get_existing_challans,
                 }
    
    def create_unpaid_challans(self, cr, uid, student_id, category, challan_type, month_ids):
        _logger.warning("Deprecated ............................................................................")
        student_id = self.pool.get('sms.student').search(cr,uid,[('id','=',student_id[0])])
        class_id = self.pool.get('sms.student').browse(cr,uid,student_id)[0].current_class.id
        self.pool.get('smsfee.receiptbook').check_fee_challans_issued(cr, uid, class_id, student_id[0], category, challan_type, month_ids)
        return True

    def print_singlestudent_unpaidfee_report(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        selected_months = thisform['unpaidfee_months_id']
        if thisform['category'] == 'Academics':
            #--------------------------------------------------------------------------
            if thisform['fee_receiving_type'] == 'Full':
                self.create_unpaid_challans(cr, uid, thisform['student_id'], 'Academics', 'Full', None)
            elif thisform['fee_receiving_type'] == 'Partial':
                self.create_unpaid_challans(cr, uid, thisform['student_id'], 'Academics', 'Partial', selected_months)
            #--------------------------------------------------------------------------
            report = 'smsfee_stu_unpaidfee_receipt_name'
            #--------------------------------------------------------------------------
        elif thisform['category'] == 'Transport':
            #--------------------------------------------------------------------------
            if thisform['fee_receiving_type'] == 'Full':
                self.create_unpaid_challans(cr, uid, thisform['student_id'], 'Transport', 'Full', None)
            elif thisform['fee_receiving_type'] == 'Partial':
                self.create_unpaid_challans(cr, uid, thisform['student_id'], 'Transport', 'Partial', selected_months)
            #--------------------------------------------------------------------------
            report = 'smstransport_stu_unpaidtransportfee_receipt'
            #--------------------------------------------------------------------------
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