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

    def check_class_student(self, cr, uid, thisform):
        student_id = self.pool.get('sms.student').search(cr, uid, [('id','=',thisform['student_id'][0])])
        student_rec = self.pool.get('sms.student').browse(cr, uid, student_id)
        for rec in student_rec:
            class_id = rec.current_class.id
        return class_id

    def check_feestructure_student(self, cr, uid, thisform):
        student_id = self.pool.get('sms.student').search(cr, uid, [('id','=',thisform['student_id'][0])])
        student_rec = self.pool.get('sms.student').browse(cr, uid, student_id)
        for rec in student_rec:
            class_id = rec.fee_type.id
        return class_id
    
    def collect_advancefee_student(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        class_id = self.check_class_student(cr, uid, thisform)
        feestructure_id = self.check_feestructure_student(cr, uid, thisform)
        classwise_fs_id = self.pool.get('smsfee.classes.fees').search(cr, uid, [('academic_cal_id','=',class_id),('fee_structure_id','=',feestructure_id)])
        class_feestruct_lines_id = self.pool.get('smsfee.classes.fees.lines').search(cr, uid, [('parent_fee_structure_id','=', classwise_fs_id),('fee_type','in',[thisform['fee_types'][0]])])
        class_feestruct_lines_obj = self.pool.get('smsfee.classes.fees.lines').browse(cr, uid, class_feestruct_lines_id)
        for record in class_feestruct_lines_obj:
            months_ids = self.pool.get('sms.session.months').search(cr, uid, [('id','in', thisform['fee_months'])])
            months_objs = self.pool.get('sms.session.months').browse(cr, uid, months_ids)
            for obj in months_objs:
                collecting_advance_fee = self.pool.get('smsfee.studentfee').insert_student_monthly_non_monthlyfee(cr, uid, thisform['student_id'][0], class_id, record, obj.id)
                if collecting_advance_fee:
                    _logger.info("Advance Fee From Student " + str(collecting_advance_fee) + " Made By " + str(uid))
        return True
    
class_student_advancefee_collect()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: