from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_student_advancefee_collect(osv.osv_memory):
    
    def _get_student(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.student_advancefee_collect"
    _description = "Advance Fee Collection From Student"
    _columns = {
              'student_id'  :   fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'fee_types'   :   fields.many2many('smsfee.feetypes', 'advancefee_std_feetype_rel', 'feetype_id', 'advancefee_id', 'Fee Type', domain="[('subtype','=','Monthly_Fee')]"),
              'fee_months'   :   fields.many2many('sms.session.months', 'advancefee_std_months_rel', 'months_id', 'advancefee_id', 'Months'),
               }
    _defaults = {
                 'student_id':_get_student,
                 }

    def check_classwise_fee_structure(self, cr, uid, thisform):
        
        student_id = self.pool.get('sms.student').search(cr, uid, [('id','=',thisform['student_id'][0])])
        student_rec = self.pool.get('sms.student').browse(cr, uid, student_id)
        for rec in student_rec:
            class_feestruct_id = self.pool.get('smsfee.classes.fees').search(cr, uid, [('academic_cal_id','=',rec.current_class.id),('fee_structure_id','=',rec.fee_type.id)])
            print "-----",class_feestruct_id
            class_feestruct_lines_id = self.pool.get('smsfee.classes.fees.lines').search(cr, uid, [('parent_fee_structure_id','=',class_feestruct_id),('fee_type','=',thisform['fee_types'][0])])
            class_feestruct_lines_obj = self.pool.get('smsfee.classes.fees.lines').browse(cr, uid, class_feestruct_lines_id)
            print "++++++",class_feestruct_lines_obj
        print alpha
        return True
    
    def collect_advancefee_student(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        calling_check1 = self.check_classwise_fee_structure(cr, uid, thisform)
        report = 'smsfee_print_three_student_per_page'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.fees',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
    
class_student_advancefee_collect()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: