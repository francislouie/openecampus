from openerp.osv import fields, osv

class sms_class_subject_list(osv.osv_memory):
    
    def get_exam_offered(self, cr, uid, ids):
        #return {'domain': {'academiccalendar_id': [('id','in', [])]}, 'value': {'exam_offered': ids['active_id']}}
        return ids['active_id']
    
    _name = "sms.class.subject.list"
    _description = "Class Subject Lists" 
    _columns = {
                'session': fields.many2one('sms.academics.session','Academic session'),
              }
    _defaults = {}
    
    def print_list(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        print "go to report**************************"
        
        report = 'sms.report.class.subject.list'
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.academiccalendar',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    

sms_class_subject_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: