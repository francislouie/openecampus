from openerp.osv import fields, osv

class sms_wizard_student_transfer_in(osv.osv_memory):

    def _get_student(self, cr, uid, ids):
        obj = self.pool.get('sms.transfer.in.out').browse(cr, uid, ids['active_ids'])[0]
        if obj.transfer_mode == 'transfer_out':
            print obj,"************",obj.student_id
            std_id =  obj.student_id.id
            return std_id
        return None
    
    def _get_student_class(self, cr, uid, ids):
        current_obj = self.pool.get('sms.transfer.in.out').browse(cr, uid, ids['active_ids'])[0]
        return current_obj.acd_cal.id
    
    def _get_transfer_mode(self, cr, uid, ids):
        current_obj = self.pool.get('sms.transfer.in.out').browse(cr, uid, ids['active_ids'])[0]
        if current_obj.transfer_mode == 'transfer_out':
            return 'Transfer Out'
        else:
            return 'Transfer In'
    
    _name = "sms.wizard.student.transfer.in"
    _description = "Student transfer"
    _columns ={'txt': fields.text('Reason', required = True),
              'student': fields.many2one('sms.student', 'Student', readonly = True),
              'current_class': fields.many2one('sms.academiccalendar','Class',readonly = True),
               }
    _defaults = {'txt': 'Are you sure you want to transfer student',
                 'student':_get_student,
                 'current_class':_get_student_class,
                'txt':_get_transfer_mode,
                  }
    
    def print_d(self, cr, uid, ids, data):
        current_obj = self.pool.get('sms.transfer.in.out').browse(cr, uid, data['active_ids'])[0]
        
        if current_obj.transfer_mode == 'transfer_in':
            _id = self.pool.get('student.admission.register').create(cr ,uid ,{'student_class':current_obj.acd_cal.id,
                                                                               'name':current_obj.student_id.name})
            self.pool.get('sms.transfer.in.out').write(cr ,uid ,data['active_ids'],{'state':'Confirm'})
            if _id:
                return {
                    'name':'Transfer In And Admitted Student',
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model':'student.admission.register',
                    'type':'ir.actions.act_window',
                    'res_id':_id,
                    }       
        else:
            withdraw_obj = self.pool.get('withdraw.student').create(cr ,uid ,{'student':current_obj.student_id.id,
                                                                              'withdraw_type': 'slc',
                                                                              'reason_withdraw':current_obj.transfer_out_reason  ,
                                                                              'transfer':True})
            self.pool.get('sms.transfer.in.out').write(cr ,uid ,data['active_ids'],{'state':'Confirm'})
            if withdraw_obj:
                return {        
                    'name'      : 'Transfer Out And Withdraw Student',
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'withdraw.student',
                    'res_id'    : withdraw_obj,
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'target'    : 'new'
                    }
    
sms_wizard_student_transfer_in()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:







