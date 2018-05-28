from openerp.osv import fields, osv
import datetime

class add_exam_class(osv.osv_memory):
    
   
    def _get_exam(self, cr, uid, ids):
        examobj = self.browse(cr, uid, ids['active_id'])
        exam_id =  examobj.id
        return exam_id
#     def _get_exam_test(self, cr, uid, ids):
#         examobj = self.browse(cr, uid, ids['active_id'])
#         exam_id =  examobj.id
#         ids=[80,68,70]
#         domain = "[('id','in',["+','.join(map(str, ids))+"])]"
#         return  ids
#     def _get_domain(self, cr, uid, ids, field_name, arg, context=None):
#         print"_get domanin method is called"
#         record_id = ids[0] 
#         
#         ids=[80,68,70]
#         domain = "[('id','in',["+','.join(map(str, ids))+"])]"
#         return {record_id: ids}
    
    _name = "add.exam.class"
    _description = "Exam Date Sheet"
    _columns = { 
                 'exam_offered': fields.many2one('sms.exam.offered', 'Select Offered Exam', domain="[('state','in',['Active','Draft'])]", required=True, readonly=True),
                 'academiccalendar':fields.many2one('sms.academiccalendar', 'Class',domain="[('state','=','Active')]", required=True),
                 'subject_marks':fields.integer('Subjects Marks',required=True),
              }
    
    _defaults = {
            'subject_marks': 100,
            'exam_offered':_get_exam,
         
           }
    
    def add_class(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        exam_offered = thisform['exam_offered'][0]
        aca_cal_id = thisform['academiccalendar'][0]
        subject_marks = thisform['subject_marks']
        exists = self.pool.get('sms.exam.datesheet').search(cr,uid, [('academiccalendar','=',aca_cal_id),('exam_offered','=',exam_offered)])
        print"exist",exists
        if  exists:
            raise osv.except_osv(('This class is already Available'), (''))
        else:
            exmds_id = self.pool.get('sms.exam.datesheet').create(cr,uid,{
                                'academiccalendar': aca_cal_id,
                                'status': 'Active',
                                'start_date':datetime.date.today(),
                                'exam_offered': exam_offered,
                               })
            return exmds_id
    
    
    
    
        
add_exam_class()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: