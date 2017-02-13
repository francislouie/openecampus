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
    
    def collect_advancefee_student(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
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