from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class smsfee_wizard_student_feetype_list(osv.osv_memory):
    
    
    _name = "student.feetype.list"
    _description = "admits student in a selected class"
    _columns = {
              'report_type':fields.selection([('summary','Summary'),('full_detail','Full Detail')],'Select Option'),
              'session': fields.many2one('sms.academics.session','Academic session' ),
              'acd_cal': fields.many2many('sms.academiccalendar','academiccalendar_class_subject','self_id','academiccalendar_id','Class'),
              'fee_type':fields.many2one('smsfee.feetypes','Feetype'),
               }
    _defaults = {}
    
    
    def print_fee_report_challan(self, cr, uid, ids, data):
        
        thisform = self.read(cr, uid, ids)[0]
        if thisform:
            print "**********",thisform
            raise osv.except_osv(('Ct'), ('h'))
        else:
            thisform = self.read(cr, uid, ids)[0]
            self.create_unpaid_challans(cr, uid, thisform['class_id'])
            report = 'smsfee.student.fee.type.list'        
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
smsfee_wizard_student_feetype_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: