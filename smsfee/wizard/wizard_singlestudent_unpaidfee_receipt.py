from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_singlestudent_unpaidfee_receipt(osv.osv_memory):
    """
    This wizard is used to print sinlge student challans for academics and transport, this wizard called a parser that generated academics and trnsport
    challans for single student and whole class. Please note that in this case that parser will print challans for single students
    --Last Updated: 23 OCT 17 By Shahid
      
    
    """
            
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

        
    _name = "class.singlestudent_unpaidfee_receipt"
    _description = "Single Student's Unpaid Fee Receipt"
    _columns = {
              'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category'),
              'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Fine After Due Date'),
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
        category = thisform['category']
        #--------------------------------------------------------------------------
        if thisform['fee_receiving_type'] == 'Full':
            self.create_unpaid_challans(cr, uid, thisform['student_id'], category, 'Full', None)
        elif thisform['fee_receiving_type'] == 'Partial':
            self.create_unpaid_challans(cr, uid, thisform['student_id'], category, 'Partial', selected_months)
        #--------------------------------------------------------------------------
        report = 'smsfee_print_one_student_per_page'
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