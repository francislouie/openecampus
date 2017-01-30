from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class class_student_fee_collect(osv.osv_memory):
    
    def _get_student(self, cr, uid, ids):
        print 'calling wizard'
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.student_fee_collect"
    _description = "Student's Fee Collection"
    _columns = {
              'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
              'challan_id': fields.many2one('smsfee.receiptbook', 'Challan', domain="[('state','=','fee_calculated')]", help="Challan"),
               }
    _defaults = {'student_id':_get_student}

    def action_pay_student_fee(self, cr, uid, ids, context):
        ctx = {}
        thisform = self.read(cr, uid, ids)[0]        
        print "-----",thisform['student_id']
        for f in self.pool.get('sms.student').browse(cr, uid, thisform['student_id']):
            if not context:
                ctx = {
                'student_id':f.id,
                'student_class_id':f.current_class.id,
                'session_id':f.current_class.acad_session_id.id,
                'fee_structure_id':f.fee_type.id
        #          'student_class_id': [(0, 0, {'product_id': product_id, 'product_qty': 1})],   
                }
            else:
                ctx = context
                ctx['student_id'] = f.id
                ctx['student_class_id'] = f.current_class.id,
                ctx['fee_structure_id'] = f.fee_type.id
                ctx['session_id'] = f.current_class.acad_session_id.id
            print "-----",ctx
#         resource_id = pooler_.get('cms.partner_tax_applied').\
#                               create(cr, uid, {'name':fiscal_year,
#                                              'partner_type':parnter_type,
#                                              'state':'Draft',
#                                              'draft_by':uid,
#                                              'draft_date':date.today()}, context=context)

        #------------------------------ Extract Form View of the object ----------------------------
#         get_view_sql = """SELECT id,name FROM ir_ui_view
#                         WHERE model= 'sms.student'
#                         AND name = 'student.form'"""
#         cr.execute(get_view_sql)
#         object_view = cr.fetchone()

        view_id = self._id_get(cr, uid, 'ir.ui.view', 'student.form', 'Student Fee')
        
        result = {
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': [view_id],
        'res_id' : ids[0], # id of the object to which to redirected
        'res_model': 'class.student_fee_collect', # object name
        'type': 'ir.actions.act_window',
        'context': ctx,
        'target': 'new', # if you want to open the form in new tab
        }        
                  
#         'type': 'ir.actions.act_window',
#         'name': 'Student Fee Collection',
#         'res_model': 'smsfee.receiptbook',
#         'view_type': 'form',
#         'view_mode': 'form',
#        'res_id': resource_id
#         'view_type': 'form',
#         'view_mode': 'form',
#         'view_id': object_view,
#         'nodestroy': True,
#         'target': 'new',
#         'context': ctx,
#        }
        return result 
    
class_student_fee_collect()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: